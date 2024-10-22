#!/usr/bin/env bash
set -e  # Exit on error
set -x  # Print commands for debugging

echo "Starting build process..."
echo "HOME directory is: $HOME"
echo "Current user: $(whoami)"
echo "Current directory: $PWD"

# Save the project root
PROJECT_ROOT=$PWD

# Create chrome directory in project folder
CHROME_DIR="/opt/render/chrome"
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
mv chromedriver $CHROME_DIR/
CHROMEDRIVER_PATH="$CHROME_DIR/chromedriver"
rm chromedriver_linux64.zip

# Print file permissions and test executables
echo "Checking file permissions..."
ls -l $CHROME_BIN
ls -l $CHROMEDRIVER_PATH
ls -l $CHROME_DIR/lib/libssl.so.1.1

# Create environment variables file
cat << EOF > $PROJECT_ROOT/set_env.sh
#!/usr/bin/env bash
export CHROME_BIN="$CHROME_BIN"
export CHROMEDRIVER_PATH="$CHROMEDRIVER_PATH"
export PATH="$CHROME_DIR:\$PATH"
export LD_LIBRARY_PATH="$CHROME_DIR/lib:\$LD_LIBRARY_PATH"
export PYTHONPATH="$PROJECT_ROOT:\$PYTHONPATH"
export CHROME_FLAGS="--no-sandbox --headless --disable-gpu --disable-dev-shm-usage --disable-software-rasterizer --remote-debugging-port=9222 --disable-features=VizDisplayCompositor"
EOF
chmod +x $PROJECT_ROOT/set_env.sh

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