#!/usr/bin/env bash

# Update package list
apt-get update

# Install wget and unzip
apt-get install -y wget unzip

# Install Chromium and ChromeDriver
apt-get install -y chromium chromium-driver

# Verify installations
echo "Verifying installations..."
which chromium
which chromedriver

# Create directory in /tmp (which is writable)
mkdir -p /tmp/chrome
chmod 777 /tmp/chrome

# Create symlinks in the writable directory
ln -sf $(which chromium) /tmp/chrome/chromium
ln -sf $(which chromedriver) /tmp/chrome/chromedriver

# Install Python requirements
pip install -r requirements.txt

# Print final paths
echo "Final verification:"
ls -l /tmp/chrome/