#!/usr/bin/env bash
set -e  # Exit on error
set -x  # Print commands for debugging

echo "Starting build process..."
echo "HOME directory is: $HOME"
echo "Current user: $(whoami)"
echo "Current directory: $PWD"

# Save the project root
PROJECT_ROOT=$PWD

# Create chrome directory in user's home directory
CHROME_DIR="$HOME/chrome"
mkdir -p $CHROME_DIR
cd $CHROME_DIR

# Create lib directory for SSL
LIB_DIR="$HOME/lib"
mkdir -p $LIB_DIR

# Install libssl1.1 in user directory
echo "Installing libssl1.1..."
wget http://archive.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.1f-1ubuntu2_amd64.deb
dpkg -x libssl1.1_1.1.1f-1ubuntu2_amd64.deb .
mv usr/lib/x86_64-linux-gnu/libssl.so.1.1 $LIB_DIR/
mv usr/lib/x86_64-linux-gnu/libcrypto.so.1.1 $LIB_DIR/
rm -rf usr etc
rm libssl1.1_1.1.1f-1ubuntu2_amd64.deb

echo "Installing Python requirements first..."
pip install -r $PROJECT_ROOT/requirements.txt

# Download Chrome binary directly from Google
echo "Downloading Chrome..."
CHROME_DEB="google-chrome-stable_current_amd64.deb"
if [ ! -f "$CHROME_DEB" ]; then
    wget -q "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"
fi

# Set up Chrome without running it
echo "Setting up Chrome..."
mkdir -p chrome-linux
dpkg -x $CHROME_DEB chrome-linux/
CHROME_BIN="$CHROME_DIR/chrome-linux/opt/google/chrome/chrome"
chmod +x $CHROME_BIN || true

# Set up ChromeDriver without version detection
echo "Setting up ChromeDriver..."
CHROMEDRIVER_PATH="$CHROME_DIR/chromedriver"
if [ ! -f "$CHROMEDRIVER_PATH" ]; then
    wget -q "https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip"
    unzip -q chromedriver_linux64.zip
    chmod +x chromedriver
fi

# Add chromedriver directory to PATH
export PATH="$CHROME_DIR:$PATH"
# Add lib directory to LD_LIBRARY_PATH
export LD_LIBRARY_PATH="$LIB_DIR:$LD_LIBRARY_PATH"

# Clean up downloaded files
rm -f $CHROME_DEB chromedriver_linux64.zip || true

# Create required directories
mkdir -p $HOME/.chrome-user-data

# Create environment setup script
cat << EOF > $PROJECT_ROOT/set_env.sh
#!/usr/bin/env bash
export CHROME_BIN="$CHROME_BIN"
export CHROMEDRIVER_PATH="$CHROMEDRIVER_PATH"
export CHROME_USER_DATA_DIR="$HOME/.chrome-user-data"
export PATH="$CHROME_DIR:\$PATH"
export LD_LIBRARY_PATH="$LIB_DIR:\$LD_LIBRARY_PATH"
export CHROME_FLAGS="--no-sandbox --headless --disable-gpu --disable-dev-shm-usage --disable-software-rasterizer --remote-debugging-port=9222 --disable-features=VizDisplayCompositor"
EOF
chmod +x $PROJECT_ROOT/set_env.sh

# Print debug information
echo "Listing chrome directory contents:"
ls -la $CHROME_DIR
echo "Listing lib directory contents:"
ls -la $LIB_DIR

# Verify installations
echo "Verifying installations..."
echo "Chrome location: $CHROME_BIN"
if [ -f "$CHROME_BIN" ]; then
    echo "Chrome binary found ✓"
    ls -l "$CHROME_BIN"
else
    echo "Chrome binary not found ✗"
fi

echo "ChromeDriver location: $CHROMEDRIVER_PATH"
if [ -f "$CHROMEDRIVER_PATH" ]; then
    echo "ChromeDriver found ✓"
    ls -l "$CHROMEDRIVER_PATH"
else
    echo "ChromeDriver not found ✗"
fi

echo "SSL library location:"
ls -l $LIB_DIR/libssl.so.1.1 || echo "SSL library not found ✗"

# Return to project directory
cd $PROJECT_ROOT

echo "Build process complete."