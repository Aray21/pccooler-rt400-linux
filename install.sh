#!/bin/bash
set -e

echo "Installing PCCOOLER RT400 Linux Temperature Monitor..."

# Check for Arch/CachyOS
if command -v pacman &> /dev/null; then
    echo "Detected Arch Linux / CachyOS"
    sudo pacman -S --needed --noconfirm python-pyusb

# Check for Debian/Ubuntu
elif command -v apt-get &> /dev/null; then
    echo "Detected Debian/Ubuntu"
    sudo apt-get update
    sudo apt-get install -y python3-usb python3-pip

else
    echo "ERROR: Unsupported Linux distribution."
    exit 1
fi

echo "Installing Python service..."

sudo install -Dm755 pccooler_sync.py \
    /usr/local/bin/pccooler_sync.py

echo "Installing systemd service..."

sudo install -Dm644 pccooler.service \
    /etc/systemd/system/pccooler.service

echo "Reloading systemd..."

sudo systemctl daemon-reload

echo "Enabling service..."

sudo systemctl enable pccooler.service

echo "Restarting service..."

sudo systemctl restart pccooler.service

echo
echo "=========================================="
echo "PCCOOLER RT400 installation complete!"
echo "=========================================="
echo
echo "Service status:"
sudo systemctl --no-pager --full status pccooler.service
echo
echo "The RT400 should now display the live CPU temperature."
