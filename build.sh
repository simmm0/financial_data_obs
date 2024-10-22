#!/usr/bin/env bash

echo "Starting build process..."

# Update package list and install dependencies
apt-get update
apt-get install -y wget unzip sudo libxss1 libappindicator1 libindicator7 libssl1.1 xvfb

# Set up Chrome
echo "Setting up Chrome..."
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
dpkg -i google-chrome-stable_current_amd64.deb || apt-get install -f -y
rm google-chrome-stable_current_amd64.deb

# Get Chrome version and download matching ChromeDriver
CHROME_VERSION=$(google-chrome --version | cut -d ' ' -f 3)
echo "Chrome version: $CHROME_VERSION"
CHROMEDRIVER_VERSION=$(wget -qO- "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION%%.*}")
echo "ChromeDriver version: $CHROMEDRIVER_VERSION"

# Set up ChromeDriver
echo "Setting up ChromeDriver..."
wget "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
unzip chromedriver_linux64.zip
mv chromedriver /usr/bin/
chmod +x /usr/bin/chromedriver
rm chromedriver_linux64.zip

# Install Python requirements
echo "Installing Python requirements..."
pip install -r requirements.txt

# Verify installations
echo "Verifying installations..."
echo "Chrome version:"
google-chrome --version
echo "ChromeDriver version:"
chromedriver --version

# Print locations
echo "Binary locations:"
which google-chrome
which chromedriver

# Set environment variables
export CHROME_BIN=/usr/bin/google-chrome
export CHROMEDRIVER_PATH=/usr/bin/chromedriver

echo "Build process complete."