# PCCOOLER RT400 Linux Temperature Monitor

PCCOOLER's software for the RT400 Digital only runs on Windows. This lightweight Linux background service reads your CPU temperature from `hwmon` and sends it directly to the RT400 display over USB.

## Features

- Real-time CPU temperature display
- Native Linux support
- Runs automatically in the background
- Starts automatically after boot
- Automatically reconnects if the RT400 USB device temporarily disappears
- Supports temperatures from 0°C to 999°C
- Lightweight and low CPU usage

## Supported devices

| Device | Status |
|---|---|
| PCCOOLER RT400 Digital | Tested |
| Other PCCOOLER digital-display models | Untested, reports welcome |

Own a similar model? Run `lsusb`, then open an issue with your USB ID and whether it works.

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
