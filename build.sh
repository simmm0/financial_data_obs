#!/usr/bin/env bash
set -e  # Exit on error
set -x  # Print commands for debugging

echo "Starting build process..."
echo "HOME directory is: $HOME"
echo "Current user: $(whoami)"
echo "Current directory: $PWD"

# Save the project root
PROJECT_ROOT=$PWD

# Create chrome directory structure
CHROME_DIR="$PROJECT_ROOT/.chrome"
mkdir -p $CHROME_DIR
cd $CHROME_DIR

# Create lib directory for SSL libraries
mkdir -p $CHROME_DIR/lib

# Install SSL libraries
echo "Installing SSL libraries..."
wget http://archive.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.1f-1ubuntu2_amd64.deb
dpkg -x libssl1.1_1.1.1f-1ubuntu2_amd64.deb .
mv usr/lib/x86_64-linux-gnu/libssl.so.1.1 $CHROME_DIR/lib/
mv usr/lib/x86_64-linux-gnu/libcrypto.so.1.1 $CHROME_DIR/lib/
rm -rf usr etc
rm libssl1.1_1.1.1f-1ubuntu2_amd64.deb

echo "Installing Python requirements..."
pip install -r $PROJECT_ROOT/requirements.txt

# Download and set up Chrome
echo "Downloading Chrome..."
wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
mkdir -p chrome-linux
dpkg -x google-chrome-stable_current_amd64.deb chrome-linux/
CHROME_BIN="$CHROME_DIR/chrome-linux/opt/google/chrome/chrome"
chmod +x $CHROME_BIN || true
rm google-chrome-stable_current_amd64.deb

# Get Chrome version and download matching ChromeDriver
echo "Getting Chrome version..."
CHROME_VERSION=$($CHROME_BIN --version | cut -d ' ' -f 3 | cut -d '.' -f 1)
echo "Chrome version: $CHROME_VERSION"

echo "Setting up ChromeDriver..."
CHROMEDRIVER_PATH="$CHROME_DIR/chromedriver"

# Download latest ChromeDriver for Chrome 130
wget -q "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/130.0.6723.69/linux64/chromedriver-linux64.zip"
unzip -q chromedriver-linux64.zip
chmod +x chromedriver-linux64/chromedriver
mv chromedriver-linux64/chromedriver $CHROMEDRIVER_PATH
rm -rf chromedriver-linux64 chromedriver-linux64.zip

# Set directory permissions
chmod -R 755 $CHROME_DIR

# Verify installations and print debug info
echo "Verifying installations..."
echo "Chrome directory structure:"
ls -R $CHROME_DIR

echo "Chrome binary:"
ls -la $CHROME_BIN || echo "Chrome binary not found!"

echo "ChromeDriver:"
ls -la $CHROMEDRIVER_PATH || echo "ChromeDriver not found!"

echo "SSL libraries:"
ls -la $CHROME_DIR/lib/ || echo "SSL libraries not found!"

# Create environment variables file
cat << EOF > $PROJECT_ROOT/set_env.sh
#!/usr/bin/env bash
export CHROME_BIN="$CHROME_BIN"
export CHROMEDRIVER_PATH="$CHROMEDRIVER_PATH"
export PATH="$CHROME_DIR:\$PATH"
export LD_LIBRARY_PATH="$CHROME_DIR/lib:\$LD_LIBRARY_PATH"
export PYTHONPATH="$PROJECT_ROOT"
export CHROME_FLAGS="--no-sandbox --headless --disable-gpu --disable-dev-shm-usage --disable-software-rasterizer --remote-debugging-port=9222 --disable-features=VizDisplayCompositor"
EOF
chmod +x $PROJECT_ROOT/set_env.sh

# Test ChromeDriver
echo "Testing ChromeDriver..."
if [ -x "$CHROMEDRIVER_PATH" ]; then
    echo "ChromeDriver is executable"
    $CHROMEDRIVER_PATH --version || echo "ChromeDriver version check failed"
else
    echo "ChromeDriver is not executable"
    ls -l $CHROMEDRIVER_PATH
fi

cd $PROJECT_ROOT
echo "Build process complete."