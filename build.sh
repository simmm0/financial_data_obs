#!/usr/bin/env bash
set -e  # Exit on error

echo "Starting build process..."

# Store the project root directory
PROJECT_ROOT="$PWD"
echo "Project root: $PROJECT_ROOT"

# Create a directory in /tmp (which is writable)
mkdir -p /tmp/chrome
cd /tmp/chrome

# Download and set up Chrome
echo "Downloading Chrome..."
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
dpkg -x google-chrome-stable_current_amd64.deb .

# Set Chrome version
CHROME_VERSION="114"
echo "Using Chrome version: $CHROME_VERSION"

# Download and set up ChromeDriver
echo "Downloading ChromeDriver..."
wget -q "https://chromedriver.storage.googleapis.com/${CHROME_VERSION}.0.5735.90/chromedriver_linux64.zip"
unzip -q chromedriver_linux64.zip
chmod +x chromedriver

# Create user bin directory and symlinks
mkdir -p $HOME/bin
ln -sf /tmp/chrome/usr/bin/google-chrome $HOME/bin/google-chrome
ln -sf /tmp/chrome/chromedriver $HOME/bin/chromedriver

# Add to PATH
export PATH="$HOME/bin:$PATH"
export CHROME_BIN="$HOME/bin/google-chrome"
export CHROMEDRIVER_PATH="$HOME/bin/chromedriver"

# Return to project directory and install Python requirements
cd "$PROJECT_ROOT"
echo "Installing Python requirements from: $PROJECT_ROOT"
pip install -r requirements.txt

# Verify installations
echo "Verifying installations..."
echo "Chrome location:"
which google-chrome || echo "Chrome not found in PATH"
echo "Chrome binary exists:"
ls -l $HOME/bin/google-chrome || echo "Chrome binary not found"

echo "ChromeDriver location:"
which chromedriver || echo "ChromeDriver not found in PATH"
echo "ChromeDriver exists:"
ls -l $HOME/bin/chromedriver || echo "ChromeDriver not found"

echo "Directory contents:"
echo "/tmp/chrome:"
ls -la /tmp/chrome
echo "$HOME/bin:"
ls -la $HOME/bin

echo "Environment variables:"
echo "PATH=$PATH"
echo "CHROME_BIN=$CHROME_BIN"
echo "CHROMEDRIVER_PATH=$CHROMEDRIVER_PATH"
echo "PWD=$PWD"

echo "Build process complete."