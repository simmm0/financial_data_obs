import sys
import os
import traceback
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def get_chrome_options(chrome_binary):
    chrome_options = Options()
    chrome_options.binary_location = chrome_binary
    
    # Get additional flags from environment variable
    chrome_flags = os.getenv('CHROME_FLAGS', '').split()
    if chrome_flags:
        for flag in chrome_flags:
            if flag not in ['--headless', '--no-sandbox', '--disable-gpu']:  # Avoid duplicates
                chrome_options.add_argument(flag)
    
    # Required arguments
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    
    # Additional required arguments
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-software-rasterizer')
    chrome_options.add_argument('--disable-features=VizDisplayCompositor')
    chrome_options.add_argument('--disable-features=NetworkService')
    chrome_options.add_argument('--disable-features=IsolateOrigins,site-per-process')
    chrome_options.add_argument('--disable-setuid-sandbox')
    chrome_options.add_argument('--disable-webgl')
    chrome_options.add_argument('--no-first-run')
    
    # Set window size and user agent
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.90 Safari/537.36')
    
    return chrome_options

def get_env_vars():
    """Get environment variables with proper checks"""
    chrome_dir = "/opt/render/project/.chrome"  # Use absolute path
    
    env_vars = {
        'chrome_binary': os.getenv('CHROME_BIN', os.path.join(chrome_dir, 'chrome-linux/opt/google/chrome/chrome')),
        'chromedriver_path': os.getenv('CHROMEDRIVER_PATH', os.path.join(chrome_dir, 'chromedriver')),
        'python_path': os.getenv('PYTHONPATH', '/opt/render/project/src'),
        'is_render': os.getenv('RENDER', 'false').lower() == 'true'
    }
    
    # Add chrome directory to PATH
    os.environ['PATH'] = f"{chrome_dir}:{os.environ.get('PATH', '')}"
    
    # Add lib directory to LD_LIBRARY_PATH
    os.environ['LD_LIBRARY_PATH'] = f"{os.path.join(chrome_dir, 'lib')}:{os.environ.get('LD_LIBRARY_PATH', '')}"
    
    logging.info(f"Environment variables: {env_vars}")
    logging.info(f"PATH: {os.environ['PATH']}")
    logging.info(f"LD_LIBRARY_PATH: {os.environ['LD_LIBRARY_PATH']}")
    
    return env_vars

def get_json_url():
    """Get the JSON export URL from the calendar page"""
    url = "https://www.forexfactory.com/calendar"
    
    env_vars = get_env_vars()
    chrome_options = get_chrome_options(env_vars['chrome_binary'])
    
    try:
        service = Service(executable_path=env_vars['chromedriver_path'])
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(url)
        
        # Wait for the Weekly Export section to be visible
        wait = WebDriverWait(driver, 20)
        weekly_export = wait.until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Weekly Export')]"))
        )
        
        # Find the JSON link under Weekly Export
        json_link = driver.find_element(By.XPATH, "//div[contains(text(), 'Weekly Export')]/following::a[contains(text(), 'JSON')]")
        json_url = json_link.get_attribute('href')
        
        logging.info(f"Found JSON URL: {json_url}")
        return json_url
    
    except Exception as e:
        logging.error(f"Error finding JSON URL: {e}")
        return None
    finally:
        if 'driver' in locals():
            driver.quit()

def scrape_forex_factory_calendar():
    """Fetch and parse calendar data"""
    try:
        # First get the JSON URL
        json_url = get_json_url()
        if not json_url:
            logging.error("Could not find JSON URL")
            return []
        
        # Fetch the JSON data
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.90 Safari/537.36',
            'Accept': 'application/json',
            'Referer': 'https://www.forexfactory.com/calendar'
        }
        
        response = requests.get(json_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            try:
                data = response.json()
                logging.info("Successfully parsed JSON response")
                
                events = []
                for event in data:
                    currency = event.get('currency', '').upper()
                    if currency not in ["USD", "ALL"]:
                        continue
                    
                    event_data = {
                        "date": event.get('date', ''),
                        "time": event.get('time', 'All Day'),
                        "currency": currency,
                        "event": event.get('title', '')
                    }
                    
                    logging.info(f"Adding event: {event_data}")
                    events.append(event_data)
                
                logging.info(f"Total events found: {len(events)}")
                if events:
                    logging.info(f"First few events: {events[:2]}")
                    
                return events
                
            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse JSON response: {e}")
                return []
        else:
            logging.error(f"Failed to fetch JSON data. Status code: {response.status_code}")
            return []
            
    except Exception as e:
        logging.error(f"Error in main scraping function: {e}")
        logging.error(traceback.format_exc())
        return []

if __name__ == '__main__':
    scrape_forex_factory_calendar()