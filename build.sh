#!/usr/bin/env bash
# Install Chrome and required dependencies
apt-get update
apt-get install -y chromium-browser chromium-chromedriver

# Install Python requirements
pip install -r requirements.txt