#!/usr/bin/env bash

# Update package list and install Chromium
apt-get update
apt-get install -y chromium-browser

# Set Chrome path for Selenium
export CHROME_BIN=/usr/bin/chromium-browser