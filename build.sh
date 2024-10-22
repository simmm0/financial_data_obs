#!/usr/bin/env bash
set -e  # Exit on error

echo "Starting build process..."
echo "HOME directory is: $HOME"
echo "Current user: $(whoami)"
echo "Current directory: $PWD"

# Save the project root
PROJECT_ROOT=$PWD

# Create chrome directory in user's home directory instead of /opt
CHROME_DIR="$HOME/chrome"
mkdir -p $CHROME_DIR
cd $CHROME_DIR

echo "Installing Python requirements first..."
pip install -r $PROJECT_ROOT/requirements.txt

# Download Chrome binary directly from Google
echo "Downloading Chrome..."
wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
mkdir -p chrome-linux
dpkg -x google-chrome-stable_current_amd64.deb chrome-linux/

# Set up Chrome
echo "Setting up Chrome..."
CHROME_BIN="$CHROME_DIR/chrome-linux/opt/google/chrome/chrome"
chmod +x $CHROME_BIN

# Download ChromeDriver - using a specific version instead of detecting
echo "Downloading ChromeDriver..."
CHROMEDRIVER_VERSION="114.0.5735.90"  # Using a stable version
wget -q "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
unzip -q chromedriver_linux64.zip
chmod +x chromedriver
CHROMEDRIVER_PATH="$CHROME_DIR/chromedriver"

# Clean up downloaded files
rm google-chrome-stable_current_amd64.deb chromedriver_linux64.zip

# Create required directories
mkdir -p $HOME/.chrome-user-data

# Create a script to set environment variables at runtime
cat << EOF > $PROJECT_ROOT/set_env.sh
export CHROME_BIN="$CHROME_BIN"
export CHROMEDRIVER_PATH="$CHROMEDRIVER_PATH"
export CHROME_USER_DATA_DIR="$HOME/.chrome-user-data"

# Chrome flags for running in a containerized environment
export CHROME_FLAGS="--no-sandbox --headless --disable-gpu --disable-dev-shm-usage --disable-software-rasterizer --disable-features=VizDisplayCompositor"
EOF
chmod +x $PROJECT_ROOT/set_env.sh

# Verify installations
echo "Verifying installations..."
echo "Chrome location: $CHROME_BIN"
[ -f "$CHROME_BIN" ] && echo "Chrome binary found" || echo "Chrome binary not found"
echo "ChromeDriver location: $CHROMEDRIVER_PATH"
[ -f "$CHROMEDRIVER_PATH" ] && echo "ChromeDriver found" || echo "ChromeDriver not found"

echo "Build process complete."