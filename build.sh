#!/usr/bin/env bash

# Update package list and install dependencies
apt-get update
apt-get install -y wget unzip

# Install Chromium and ChromeDriver
apt-get install -y chromium-browser chromium-chromedriver

# Create directory for ChromeDriver
mkdir -p /opt/chromedriver

# Download specific version of ChromeDriver
wget -q "https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip"
unzip -q chromedriver_linux64.zip -d /opt/chromedriver
chmod +x /opt/chromedriver/chromedriver

# Install Python requirements
pip install -r requirements.txt