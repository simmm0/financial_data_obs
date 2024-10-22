#!/usr/bin/env bash
set -e  # Exit on error

echo "Starting build process..."
echo "HOME directory is: $HOME"
echo "Current user: $(whoami)"
echo "Current directory: $PWD"

# Create chrome directory in project folder
CHROME_DIR="/opt/render/project/chrome"
mkdir -p $CHROME_DIR
cd $CHROME_DIR

# Download and set up Chrome
echo "Downloading Chrome..."
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
dpkg -x google-chrome-stable_current_amd64.deb .

# Download and set up ChromeDriver
echo "Downloading ChromeDriver..."
CHROME_VERSION="114"
wget -q "https://chromedriver.storage.googleapis.com/${CHROME_VERSION}.0.5735.90/chromedriver_linux64.zip"
unzip -q chromedriver_linux64.zip
chmod +x chromedriver

# Move Chrome binary to final location
mv usr/bin/google-chrome google-chrome
chmod +x google-chrome

# Clean up
rm -rf usr
rm google-chrome-stable_current_amd64.deb
rm chromedriver_linux64.zip

# Set up environment variables
export CHROME_BIN="$CHROME_DIR/google-chrome"
export CHROMEDRIVER_PATH="$CHROME_DIR/chromedriver"

# Return to project directory for requirements installation
cd $PROJECT_ROOT
echo "Installing Python requirements..."
pip install -r requirements.txt

# Verify installations
echo "Verifying installations..."
echo "Chrome location:"
ls -l $CHROME_BIN || echo "Chrome binary not found"
echo "ChromeDriver location:"
ls -l $CHROMEDRIVER_PATH || echo "ChromeDriver not found"

echo "Environment variables:"
echo "CHROME_BIN=$CHROME_BIN"
echo "CHROMEDRIVER_PATH=$CHROMEDRIVER_PATH"

echo "Build process complete."