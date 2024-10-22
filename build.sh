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

# Install Python requirements
pip install -r requirements.txt

# Print installation locations
echo "Chromium location:"
whereis chromium
echo "ChromeDriver location:"
whereis chromedriver

# Create necessary directories and set permissions
mkdir -p /opt/chromedriver
chmod 777 /opt/chromedriver

# Create symlinks if needed
ln -sf $(which chromium) /usr/bin/chromium-browser
ln -sf $(which chromedriver) /opt/chromedriver/chromedriver

# Verify final paths
echo "Final verification:"
ls -l /usr/bin/chromium-browser
ls -l /opt/chromedriver/chromedriver