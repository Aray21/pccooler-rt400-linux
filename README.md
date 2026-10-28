# PCCOOLER RT400 Linux Temperature Monitor

PCCOOLER's official software for the RT400 Digital only runs on Windows. This lightweight Linux background service reads your CPU temperature from `hwmon` and sends it directly to the RT400 display over USB.

> Unofficial project, not affiliated with PCCOOLER / CPS.

## Features

- Real-time CPU temperature display
- Native Linux support
- Runs automatically in the background
- Starts automatically after boot
- Automatically reconnects if the RT400 USB device temporarily disappears
- Supports temperatures from 0°C to 999°C
- Lightweight and low CPU usage

## Official software

The official Windows app for these coolers is **CPS-Digital**, available from the PCCOOLER software page:

http://www.cpspccooler.com/software/

This project replaces it on Linux.

## Supported devices

| Device | Status |
|---|---|
| PCCOOLER RT400 Digital | Tested |

> **Note:** the RT400's controller shows up in `lsusb` as
> `1a2c:444d China Resource Semico Co., Ltd USB Gaming Keyboard`.
> The name is misleading, but that is the cooler's display controller.

### Possibly compatible (untested)

These models use the same official app (CPS-Digital) as the RT400, so they may work too, but nobody has tested them yet:

- RT500 Digital
- RT500 Digital ARGB
- RT620 Digital
- DA360 Pro ARGB Digital
- DA240 Pro ARGB Digital
- DC360 ARGB Digital
- DS360 Pro Digital
- GT360 ARGB Digital
- Digital Cell

Own one of these? Run `lsusb`, then open an issue with your model, your USB ID and whether it works. Working models will be moved to the tested list.

## Requirements

- Linux with `systemd`
- PCCOOLER RT400 Digital
- USB connection from the RT400
- Python 3
- PyUSB

The installer automatically installs the required USB Python package.

## Installation

Open a terminal inside this folder and run:

```bash
chmod +x install.sh
sudo ./install.sh
```

## Check Service Status

```bash
sudo systemctl status pccooler.service
```

A working service should show:

```
Active: active (running)
```

## View Live Logs

```bash
sudo journalctl -u pccooler.service -f
```

Example:

```
RT400 connected
RT400 <- 58 C (USB transfer: 64 bytes)
RT400 <- 57 C (USB transfer: 64 bytes)
RT400 <- 56 C (USB transfer: 64 bytes)
```

Press `Ctrl+C` to stop viewing the logs.

## Restart the Service

If you update `pccooler_sync.py` or `pccooler.service`, restart the service:

```bash
sudo systemctl daemon-reload
sudo systemctl restart pccooler.service
```

## Stop the Service

To temporarily stop the temperature display:

```bash
sudo systemctl stop pccooler.service
```

## Disable Automatic Startup

To prevent the service from starting automatically at boot:

```bash
sudo systemctl disable pccooler.service
```

To enable it again:

```bash
sudo systemctl enable pccooler.service
```

## Uninstall

To completely remove the RT400 service:

```bash
sudo systemctl disable --now pccooler.service
sudo rm -f /etc/systemd/system/pccooler.service
sudo rm -f /usr/local/bin/pccooler_sync.py
sudo systemctl daemon-reload
```

## Troubleshooting

### Service is not running

Check the service:

```bash
sudo systemctl status pccooler.service
```

Check recent logs:

```bash
sudo journalctl -u pccooler.service -n 50 --no-pager
```

### RT400 is not updating

Check that Linux detects the RT400:

```bash
lsusb | grep -i '1a2c:444d'
```

The RT400 should appear as `1a2c:444d`. Then restart the service:

```bash
sudo systemctl restart pccooler.service
```

### Check automatic startup

```bash
systemctl is-enabled pccooler.service
```

Expected output: `enabled`

## Project Files

- `install.sh`
- `pccooler_sync.py`
- `pccooler.service`
- `README.md`

Installed paths:

- `/usr/local/bin/pccooler_sync.py`
- `/etc/systemd/system/pccooler.service`

## License

MIT
