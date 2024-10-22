#!/usr/bin/env bash
set -e  # Exit on error
set -x  # Print commands for debugging

echo "Starting build process..."
echo "HOME directory is: $HOME"
echo "Current user: $(whoami)"
echo "Current directory: $PWD"
echo "Contents of /opt/render:"
ls -la /opt/render

# Save the project root
PROJECT_ROOT=$PWD

# Use an absolute path that should be writable
CHROME_DIR="/opt/render/project/.chrome"
echo "Creating Chrome directory at: $CHROME_DIR"
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

# Download and set up ChromeDriver
echo "Setting up ChromeDriver..."
wget -q "https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip"
unzip -q chromedriver_linux64.zip
chmod +x chromedriver
CHROMEDRIVER_PATH="$CHROME_DIR/chromedriver"
mv chromedriver $CHROMEDRIVER_PATH || true
rm chromedriver_linux64.zip

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

# Create .env file with the same variables
cat << EOF > $PROJECT_ROOT/.env
CHROME_BIN=$CHROME_BIN
CHROMEDRIVER_PATH=$CHROMEDRIVER_PATH
LD_LIBRARY_PATH=$CHROME_DIR/lib
PYTHONPATH=$PROJECT_ROOT
RENDER=true
EOF

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

# Final verification
echo "Final directory contents:"
echo "Project root:"
ls -la $PROJECT_ROOT
echo "Chrome directory:"
ls -la $CHROME_DIR

echo "Build process complete."