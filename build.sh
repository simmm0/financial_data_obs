#!/usr/bin/env bash

# Update package list
apt-get update

# Install Chromium and dependencies
apt-get install -y wget unzip chromium

# Create symlink for chromium-browser
ln -sf /usr/bin/chromium /usr/bin/chromium-browser

# Export paths
export CHROME_BIN=/usr/bin/chromium
export CHROMIUM_PATH=/usr/bin/chromium
export PATH="$PATH:/usr/bin"

# Install Python requirements
pip install -r requirements.txt

# Verify installations
echo "Verifying installations..."
echo "Chrome binary location:"
which chromium
echo "Chrome version:"
chromium --version || echo "Failed to get Chrome version"

# Print environment information
echo "Environment variables:"
echo "CHROME_BIN=$CHROME_BIN"
echo "CHROMIUM_PATH=$CHROMIUM_PATH"
echo "PATH=$PATH"

# List binary locations
echo "Binary locations:"
ls -l /usr/bin/chromium* || echo "No chromium binaries found"