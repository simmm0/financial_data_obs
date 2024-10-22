#!/usr/bin/env bash

# Update package list
apt-get update

# Install Chrome and required dependencies
apt-get install -y wget unzip chromium-browser

# Add Chrome to PATH
export PATH="$PATH:/usr/bin/chromium-browser"

# Install Python requirements
pip install -r requirements.txt

# Verify Chrome installation
which chromium-browser
chromium-browser --version

# Print environment information
echo "PATH: $PATH"
echo "Chrome location:"
whereis chromium-browser