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
apt-get install -y wget gnupg curl unzip libssl1.1

# Install Chrome
echo "Installing Chrome..."
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google.list
apt-get update
apt-get install -y google-chrome-stable

# Get Chrome version and download matching ChromeDriver
CHROME_VERSION=$(google-chrome --version | cut -d " " -f3 | cut -d "." -f1-3)
echo "Installed Chrome version: $CHROME_VERSION"

# Download and install ChromeDriver
echo "Installing ChromeDriver..."
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}")
echo "Matching ChromeDriver version: $CHROMEDRIVER_VERSION"
wget -q "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
unzip -q chromedriver_linux64.zip
mv chromedriver /usr/local/bin/
chmod +x /usr/local/bin/chromedriver

# Clean up downloaded files
rm chromedriver_linux64.zip

# Set up environment variables if not already set
if [ -z "$CHROME_BIN" ]; then
    export CHROME_BIN=/usr/bin/google-chrome
fi
if [ -z "$CHROMEDRIVER_PATH" ]; then
    export CHROMEDRIVER_PATH=/usr/local/bin/chromedriver
fi

# Install Python requirements
echo "Installing Python requirements..."
pip install -r requirements.txt

# Verify installations
echo "Verifying installations..."
echo "Chrome version:"
$CHROME_BIN --version || echo "Failed to get Chrome version"
echo "ChromeDriver version:"
$CHROMEDRIVER_PATH --version || echo "Failed to get ChromeDriver version"
echo "SSL library:"
ldconfig -p | grep libssl || echo "SSL library not found"

# Print final environment state
echo "Final environment:"
echo "PYTHONPATH=$PYTHONPATH"
echo "RENDER=$RENDER"
echo "CHROME_BIN=$CHROME_BIN"
echo "CHROMEDRIVER_PATH=$CHROMEDRIVER_PATH"

# Verify paths and permissions
echo "Verifying paths and permissions..."
ls -l $CHROME_BIN
ls -l $CHROMEDRIVER_PATH

echo "Build process complete."