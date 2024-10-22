#!/usr/bin/env bash

# Install Chrome and ChromeDriver
sudo apt-get update
sudo apt-get install -y chromium-browser chromium-chromedriver

# Install Python requirements
pip install -r requirements.txt