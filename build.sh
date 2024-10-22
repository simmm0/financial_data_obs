#!/usr/bin/env bash

echo "Starting build process..."

# Print initial environment state
echo "Initial environment:"
echo "PYTHONPATH=$PYTHONPATH"
echo "RENDER=$RENDER"
echo "CHROME_BIN=$CHROME_BIN"
echo "CHROMEDRIVER_PATH=$CHROMEDRIVER_PATH"

# Update package list and install dependencies
apt-get update
apt-get install -y wget gnupg curl unzip chromium chromium-driver

# Create necessary directories
mkdir -p /usr/local/bin
mkdir -p /usr/bin

# Create symlinks with proper names
ln -sf /usr/bin/chromium /usr/bin/google-chrome || echo "Failed to create Chrome symlink"
ln -sf /usr/bin/chromedriver /usr/local/bin/chromedriver || echo "Failed to create ChromeDriver symlink"

# Make sure executables are actually there
if [ ! -f "/usr/bin/chromium" ]; then
    echo "Error: Chromium not found at /usr/bin/chromium"
    apt-get install -y chromium
fi

if [ ! -f "/usr/bin/chromedriver" ]; then
    echo "Error: ChromeDriver not found at /usr/bin/chromedriver"
    apt-get install -y chromium-driver
fi

# Set correct permissions
chmod +x /usr/bin/chromium || echo "Failed to set Chrome permissions"
chmod +x /usr/bin/chromedriver || echo "Failed to set ChromeDriver permissions"

# Set up environment variables
export CHROME_BIN=/usr/bin/google-chrome
export CHROMEDRIVER_PATH=/usr/local/bin/chromedriver
export PATH=$PATH:/usr/local/bin:/usr/bin

# Install Python requirements
echo "Installing Python requirements..."
pip install -r requirements.txt

# Verify installations
echo "Verifying installations..."
echo "Chrome path exists:"
ls -l /usr/bin/chromium || echo "Chromium not found"
echo "ChromeDriver path exists:"
ls -l /usr/bin/chromedriver || echo "ChromeDriver not found"
echo "Chrome version:"
chromium --version || echo "Failed to get Chrome version"
echo "ChromeDriver version:"
chromedriver --version || echo "Failed to get ChromeDriver version"

# Print all relevant directories
echo "Directory contents:"
echo "/usr/bin:"
ls -l /usr/bin/chrom* || echo "No Chrome files in /usr/bin"
echo "/usr/local/bin:"
ls -l /usr/local/bin/chrom* || echo "No Chrome files in /usr/local/bin"

# Print final environment state
echo "Final environment:"
echo "PYTHONPATH=$PYTHONPATH"
echo "RENDER=$RENDER"
echo "CHROME_BIN=$CHROME_BIN"
echo "CHROMEDRIVER_PATH=$CHROMEDRIVER_PATH"
echo "PATH=$PATH"

echo "Build process complete."