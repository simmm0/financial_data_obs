#!/usr/bin/env bash
set -e  # Exit on error

echo "Starting build process..."
echo "HOME directory is: $HOME"
echo "Current user: $(whoami)"
echo "Current directory: $PWD"

# Save the project root
PROJECT_ROOT=$PWD

# Create chrome directory in project folder
CHROME_DIR="/opt/render/project/chrome"
mkdir -p $CHROME_DIR
cd $CHROME_DIR

# Install required dependencies
apt-get update
apt-get install -y wget unzip fonts-liberation libasound2 libatk-bridge2.0-0 \
    libatk1.0-0 libatspi2.0-0 libcairo2 libcups2 libdbus-1-3 libdrm2 \
    libgbm1 libgdk-pixbuf2.0-0 libgtk-3-0 libnspr4 libnss3 \
    libpango-1.0-0 libpangocairo-1.0-0 libx11-6 libx11-xcb1 \
    libxcb-dri3-0 libxcb1 libxcomposite1 libxcursor1 libxdamage1 \
    libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 \
    xdg-utils libglib2.0-0 libnvidia-egl-wayland1

# Download and set up Chrome
echo "Downloading Chrome..."
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
dpkg -x google-chrome-stable_current_amd64.deb .

# Copy Chrome binary to final location
echo "Setting up Chrome..."
cp -v ./opt/google/chrome/chrome ./google-chrome
chmod +x ./google-chrome

# Set up required directories
mkdir -p /tmp/.X11-unix
mkdir -p /tmp/.com.google.Chrome.{cjpalhdlnbpafiamejdnhcphjbkeiagm,eemcgdkfndhakfknompkggombfjjjeno}

# Download and set up ChromeDriver
echo "Downloading ChromeDriver..."
CHROME_VERSION="114"
wget -q "https://chromedriver.storage.googleapis.com/${CHROME_VERSION}.0.5735.90/chromedriver_linux64.zip"
unzip -q chromedriver_linux64.zip
chmod +x chromedriver

# Clean up
rm -rf usr opt etc
rm google-chrome-stable_current_amd64.deb
rm chromedriver_linux64.zip

# Set up environment variables
export CHROME_BIN="$CHROME_DIR/google-chrome"
export CHROMEDRIVER_PATH="$CHROME_DIR/chromedriver"

# Create a chrome-user-data directory
mkdir -p "$CHROME_DIR/chrome-user-data"

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

echo "Final directory contents:"
ls -la $CHROME_DIR

echo "Environment variables:"
echo "CHROME_BIN=$CHROME_BIN"
echo "CHROMEDRIVER_PATH=$CHROMEDRIVER_PATH"

echo "Build process complete."