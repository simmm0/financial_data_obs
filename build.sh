#!/usr/bin/env bash
set -e  # Exit on error
set -x  # Print commands for debugging

echo "Starting build process..."
echo "HOME directory is: $HOME"
echo "Current user: $(whoami)"
echo "Current directory: $PWD"

# Save the project root
PROJECT_ROOT=$PWD

# Create necessary directories
CHROME_DIR="$HOME/chrome"
BIN_DIR="$CHROME_DIR/bin"
LIB_DIR="$CHROME_DIR/lib"

mkdir -p $CHROME_DIR $BIN_DIR $LIB_DIR

cd $CHROME_DIR

# Install libssl1.1 in the correct location
echo "Installing libssl1.1..."
wget http://archive.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.1f-1ubuntu2_amd64.deb
dpkg -x libssl1.1_1.1.1f-1ubuntu2_amd64.deb .
mv usr/lib/x86_64-linux-gnu/libssl.so.1.1 $LIB_DIR/
mv usr/lib/x86_64-linux-gnu/libcrypto.so.1.1 $LIB_DIR/
rm -rf usr etc libssl1.1_1.1.1f-1ubuntu2_amd64.deb

echo "Installing Python requirements..."
pip install -r $PROJECT_ROOT/requirements.txt

# Set up Chrome
echo "Setting up Chrome..."
wget -q "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"
dpkg -x google-chrome-stable_current_amd64.deb chrome-linux/
CHROME_BIN="$CHROME_DIR/chrome-linux/opt/google/chrome/chrome"
chmod +x $CHROME_BIN
rm google-chrome-stable_current_amd64.deb

# Set up ChromeDriver
echo "Setting up ChromeDriver..."
wget -q "https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip"
unzip -q chromedriver_linux64.zip -d $BIN_DIR
chmod +x $BIN_DIR/chromedriver
rm chromedriver_linux64.zip

# Create environment setup script
cat << EOF > $PROJECT_ROOT/set_env.sh
#!/usr/bin/env bash
export PATH="$BIN_DIR:\$PATH"
export LD_LIBRARY_PATH="$LIB_DIR:\$LD_LIBRARY_PATH"
export CHROME_BIN="$CHROME_BIN"
export CHROMEDRIVER_PATH="$BIN_DIR/chromedriver"
export CHROME_USER_DATA_DIR="$CHROME_DIR/user-data"
export CHROME_FLAGS="--no-sandbox --headless --disable-gpu --disable-dev-shm-usage --disable-software-rasterizer --remote-debugging-port=9222 --disable-features=VizDisplayCompositor"
EOF
chmod +x $PROJECT_ROOT/set_env.sh

# Verify installations
echo "Verifying installations..."
echo "Directory structure:"
ls -R $CHROME_DIR

echo "Chrome binary: $CHROME_BIN"
[ -f "$CHROME_BIN" ] && echo "✓ Chrome binary found" || echo "✗ Chrome binary missing"

echo "ChromeDriver: $BIN_DIR/chromedriver"
[ -f "$BIN_DIR/chromedriver" ] && echo "✓ ChromeDriver found" || echo "✗ ChromeDriver missing"

echo "SSL libraries:"
[ -f "$LIB_DIR/libssl.so.1.1" ] && echo "✓ libssl.so.1.1 found" || echo "✗ libssl.so.1.1 missing"
[ -f "$LIB_DIR/libcrypto.so.1.1" ] && echo "✓ libcrypto.so.1.1 found" || echo "✗ libcrypto.so.1.1 missing"

cd $PROJECT_ROOT
echo "Build process complete."