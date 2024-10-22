#!/usr/bin/env bash

# Update package list and install dependencies
apt-get update
apt-get install -y wget gnupg curl unzip libssl1.1

# Install Chrome and ChromeDriver
CHROME_VERSION="114.0.5735.90"
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google.list
apt-get update
apt-get install -y google-chrome-stable

# Download and install ChromeDriver
wget -q "https://chromedriver.storage.googleapis.com/${CHROME_VERSION}/chromedriver_linux64.zip"
unzip -q chromedriver_linux64.zip
mv chromedriver /usr/local/bin/
chmod +x /usr/local/bin/chromedriver

# Set up environment variables
export CHROME_BIN=/usr/bin/google-chrome
export CHROMEDRIVER_PATH=/usr/local/bin/chromedriver
export PATH=$PATH:/usr/local/bin

# Install Python requirements
pip install -r requirements.txt

# Verify installations
echo "Verifying installations..."
echo "Chrome version:"
google-chrome --version || echo "Failed to get Chrome version"
echo "ChromeDriver version:"
chromedriver --version || echo "Failed to get ChromeDriver version"
echo "SSL library:"
ldconfig -p | grep libssl || echo "SSL library not found"

# Print environment information
echo "Environment variables:"
echo "CHROME_BIN=$CHROME_BIN"
echo "CHROMEDRIVER_PATH=$CHROMEDRIVER_PATH"
echo "PATH=$PATH"