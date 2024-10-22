#!/usr/bin/env bash

# Update package list and install dependencies
apt-get update
apt-get install -y wget gnupg

# Add Google Chrome repository
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google.list

# Update package list again and install Chrome
apt-get update
apt-get install -y google-chrome-stable

# Export Chrome path
export CHROME_BIN=/usr/bin/google-chrome
export PATH="$PATH:/usr/bin"

# Install Python requirements
pip install -r requirements.txt

# Verify installations
echo "Verifying installations..."
echo "Chrome binary location:"
which google-chrome
echo "Chrome version:"
google-chrome --version || echo "Failed to get Chrome version"

# Print environment information
echo "Environment variables:"
echo "CHROME_BIN=$CHROME_BIN"
echo "PATH=$PATH"

# List binary location
echo "Binary locations:"
ls -l /usr/bin/google-chrome* || echo "No chrome binaries found"