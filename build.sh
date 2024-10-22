#!/usr/bin/env bash
set -e  # Exit on error

echo "Starting build process..."

# Update package list and install dependencies
apt-get update
apt-get install -y wget curl unzip apt-transport-https ca-certificates gnupg

# Add Google Chrome repository
echo "Adding Google Chrome repository..."
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google.list

# Update again and install Chrome
echo "Installing Google Chrome..."
apt-get update
apt-get install -y google-chrome-stable
apt-get install -y xvfb libxi6 libgconf-2-4

# Get Chrome version for matching ChromeDriver
CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d. -f1)
echo "Chrome version detected: $CHROME_VERSION"

# Install ChromeDriver
echo "Installing ChromeDriver..."
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}")
echo "Installing ChromeDriver version: $CHROMEDRIVER_VERSION"
wget -q "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
unzip -q chromedriver_linux64.zip
mv chromedriver /usr/bin/
chmod +x /usr/bin/chromedriver
rm chromedriver_linux64.zip

# Install Python requirements
echo "Installing Python requirements..."
pip install -r requirements.txt

# Verify installations
echo "Verifying installations..."
echo "Checking Chrome..."
if command -v google-chrome &> /dev/null; then
    echo "Chrome is installed:"
    google-chrome --version
else
    echo "Chrome installation failed"
    exit 1
fi

echo "Checking ChromeDriver..."
if command -v chromedriver &> /dev/null; then
    echo "ChromeDriver is installed:"
    chromedriver --version
else
    echo "ChromeDriver installation failed"
    exit 1
fi

# Print locations and permissions
echo "File permissions and locations:"
ls -l /usr/bin/google-chrome*
ls -l /usr/bin/chromedriver*

# Set environment variables
export CHROME_BIN=/usr/bin/google-chrome
export CHROMEDRIVER_PATH=/usr/bin/chromedriver
echo "Environment variables set to:"
echo "CHROME_BIN=$CHROME_BIN"
echo "CHROMEDRIVER_PATH=$CHROMEDRIVER_PATH"

echo "Build process complete."