#!/usr/bin/env bash
set -e  # Exit on error

echo "Starting build process..."

# Create a directory in /tmp (which is writable)
mkdir -p /tmp/chrome
cd /tmp/chrome

# Download and set up Chrome
echo "Downloading Chrome..."
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
dpkg -x google-chrome-stable_current_amd64.deb chrome

# Get Chrome version for matching ChromeDriver
CHROME_VERSION=$(./chrome/usr/bin/google-chrome --version | awk '{print $3}' | cut -d. -f1) || CHROME_VERSION="114"
echo "Chrome version detected: ${CHROME_VERSION:-114}"

# Download and set up ChromeDriver
echo "Downloading ChromeDriver..."
wget -q "https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip"
unzip -q chromedriver_linux64.zip
chmod +x chromedriver

# Create symlinks
mkdir -p $HOME/bin
ln -s /tmp/chrome/chrome/usr/bin/google-chrome $HOME/bin/google-chrome
ln -s /tmp/chrome/chromedriver $HOME/bin/chromedriver

# Add to PATH
export PATH="$HOME/bin:$PATH"
export CHROME_BIN="$HOME/bin/google-chrome"
export CHROMEDRIVER_PATH="$HOME/bin/chromedriver"

# Install Python requirements
echo "Installing Python requirements..."
pip install -r requirements.txt

# Verify installations
echo "Verifying installations..."
echo "Chrome location:"
which google-chrome || echo "Chrome not found in PATH"
echo "ChromeDriver location:"
which chromedriver || echo "ChromeDriver not found in PATH"

echo "File permissions:"
ls -l $HOME/bin/google-chrome || echo "Chrome binary not found"
ls -l $HOME/bin/chromedriver || echo "ChromeDriver not found"

echo "Environment variables:"
echo "PATH=$PATH"
echo "CHROME_BIN=$CHROME_BIN"
echo "CHROMEDRIVER_PATH=$CHROMEDRIVER_PATH"

echo "Build process complete."