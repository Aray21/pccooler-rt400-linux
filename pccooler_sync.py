#!/usr/bin/env python3

import glob
import os
import signal
import sys
import time

import usb.core
import usb.util


VID = 0x1A2C
PID = 0x444D
INTERFACE = 1

SEND_INTERVAL = 1.0


running = True


def stop_handler(signum, frame):
    global running
    running = False


signal.signal(signal.SIGTERM, stop_handler)
signal.signal(signal.SIGINT, stop_handler)


def read_temperature():
    """
    Prefer the same common CPU hwmon drivers used by the original script.
    Return integer degrees C, or None if no usable sensor is found.
    """

    preferred = ("coretemp", "k10temp", "zenpower")

    hwmons = glob.glob("/sys/class/hwmon/hwmon*")

    # First pass: preferred CPU temperature drivers.
    for wanted in preferred:
        for hwmon in hwmons:
            try:
                with open(os.path.join(hwmon, "name"), "r") as f:
                    name = f.read().strip()
            except (OSError, IOError):
                continue

            if name != wanted:
                continue

            inputs = sorted(glob.glob(os.path.join(hwmon, "temp*_input")))

            for path in inputs:
                try:
                    value = int(open(path).read().strip()) / 1000.0
                except (OSError, IOError, ValueError):
                    continue

                if 0 < value < 150:
                    return round(value)

    # Fallback: any usable hwmon temperature.
    for hwmon in hwmons:
        for path in sorted(glob.glob(os.path.join(hwmon, "temp*_input"))):
            try:
                value = int(open(path).read().strip()) / 1000.0
            except (OSError, IOError, ValueError):
                continue

            if 0 < value < 150:
                return round(value)

    return None


def make_payload(temp):
    """
    Verified RT400 Digital temperature format.

    Byte 0: 07
    Byte 1: FF
    Byte 2: FF
    Byte 3: hundreds
    Byte 4: tens
    Byte 5: ones
    Byte 6-63: zero
    """

    temp = max(0, min(999, int(temp)))

    hundreds = temp // 100
    tens = (temp // 10) % 10
    ones = temp % 10

    payload = bytearray(64)

    payload[0] = 0x07
    payload[1] = 0xFF
    payload[2] = 0xFF
    payload[3] = hundreds
    payload[4] = tens
    payload[5] = ones

    return payload


def find_device():
    return usb.core.find(idVendor=VID, idProduct=PID)


def open_device():
    """
    Find RT400 and claim interface 1.

    The RT400 presents itself as a HID device, so Linux may have
    already attached a kernel HID driver to interface 1.
    """

    device = find_device()

    if device is None:
        return None, False

    detached = False

    try:
        if device.is_kernel_driver_active(INTERFACE):
            print("Detaching kernel driver from interface 1", flush=True)
            device.detach_kernel_driver(INTERFACE)
            detached = True
    except (usb.core.USBError, NotImplementedError):
        pass

    try:
        usb.util.claim_interface(device, INTERFACE)
    except usb.core.USBError as e:
        print(f"USB claim failed: {e}", flush=True)

        if detached:
            try:
                device.attach_kernel_driver(INTERFACE)
            except usb.core.USBError:
                pass

        return None, False

    return device, detached


def close_device(device, detached):
    if device is None:
        return

    try:
        usb.util.release_interface(device, INTERFACE)
    except usb.core.USBError:
        pass

    if detached:
        try:
            device.attach_kernel_driver(INTERFACE)
        except usb.core.USBError:
            pass

    try:
        usb.util.dispose_resources(device)
    except Exception:
        pass


def send_temperature(device, temp):
    payload = make_payload(temp)

    return device.ctrl_transfer(
        0x21,       # bmRequestType: HID class / host-to-device / interface
        0x09,       # bRequest: SET_REPORT
        0x0307,     # report type 3, report ID 7
        INTERFACE,  # interface 1
        payload
    )


def main():
    print("PCCOOLER RT400 Linux temperature service", flush=True)
    print(
        f"USB device: {VID:04X}:{PID:04X}, interface {INTERFACE}",
        flush=True,
    )

    device = None
    detached = False
    last_temp = None

    while running:

        # Reconnect if device isn't currently open.
        if device is None:

            try:
                device, detached = open_device()
            except usb.core.USBError as e:
                print(f"USB open error: {e}", flush=True)
                device = None
                detached = False

            if device is None:
                time.sleep(2)
                continue

            print("RT400 connected", flush=True)

        temp = read_temperature()

        if temp is None:
            print("No CPU temperature sensor found", flush=True)
            time.sleep(SEND_INTERVAL)
            continue

        try:
            result = send_temperature(device, temp)

            if temp != last_temp:
                print(
                    f"RT400 <- {temp} C "
                    f"(USB transfer: {result} bytes)",
                    flush=True,
                )
                last_temp = temp

        except usb.core.USBError as e:
            print(f"USB write failed: {e}; reconnecting", flush=True)

            close_device(device, detached)
            device = None
            detached = False
            last_temp = None

            time.sleep(1)
            continue

        time.sleep(SEND_INTERVAL)

    close_device(device, detached)
    print("RT400 service stopped", flush=True)


if __name__ == "__main__":
    main()
