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
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
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
    
    # Set user data directory if specified
    user_data_dir = os.getenv('CHROME_USER_DATA_DIR')
    if user_data_dir:
        chrome_options.add_argument(f'--user-data-dir={user_data_dir}')
    
    return chrome_options

def get_env_vars():
    """Get environment variables with proper checks"""
    chrome_dir = os.path.join(os.getenv('HOME', ''), '.chrome')
    
    env_vars = {
        'chrome_binary': os.getenv('CHROME_BIN', os.path.join(chrome_dir, 'chrome-linux/opt/google/chrome/chrome')),
        'chromedriver_path': os.getenv('CHROMEDRIVER_PATH', os.path.join(chrome_dir, 'chromedriver')),
        'python_path': os.getenv('PYTHONPATH', '/opt/render/project/src'),
        'is_render': os.getenv('RENDER', 'false').lower() == 'true'
    }
    
    # Ensure directories exist
    os.makedirs(chrome_dir, exist_ok=True)
    
    # Check if ChromeDriver exists and is executable
    if not os.path.exists(env_vars['chromedriver_path']):
        logging.error(f"ChromeDriver not found at {env_vars['chromedriver_path']}")
    else:
        logging.info(f"ChromeDriver found at {env_vars['chromedriver_path']}")
        if not os.access(env_vars['chromedriver_path'], os.X_OK):
            logging.error("ChromeDriver is not executable")
            try:
                os.chmod(env_vars['chromedriver_path'], 0o755)
                logging.info("Fixed ChromeDriver permissions")
            except Exception as e:
                logging.error(f"Failed to fix ChromeDriver permissions: {e}")
    
    # Add chrome directory to PATH
    os.environ['PATH'] = f"{chrome_dir}:{os.environ.get('PATH', '')}"
    
    # Add lib directory to LD_LIBRARY_PATH
    os.environ['LD_LIBRARY_PATH'] = f"{os.path.join(chrome_dir, 'lib')}:{os.environ.get('LD_LIBRARY_PATH', '')}"
    
    logging.info(f"Environment variables: {env_vars}")
    logging.info(f"PATH: {os.environ['PATH']}")
    logging.info(f"LD_LIBRARY_PATH: {os.environ['LD_LIBRARY_PATH']}")
    
    # Directory contents for debugging
    try:
        logging.info(f"Chrome directory contents: {os.listdir(chrome_dir)}")
    except Exception as e:
        logging.error(f"Could not list chrome directory: {e}")
    
    return env_vars

def scrape_forex_factory_calendar():
    url = "https://www.forexfactory.com/calendar"
    
    logging.info("Starting scrape_forex_factory_calendar function")
    env_vars = get_env_vars()
    logging.info(f"Current working directory: {os.getcwd()}")
    
    # Ensure the chromedriver exists and is executable
    if not os.path.exists(env_vars['chromedriver_path']):
        logging.error(f"ChromeDriver not found at {env_vars['chromedriver_path']}")
        return []
    
    if not os.access(env_vars['chromedriver_path'], os.X_OK):
        logging.error(f"ChromeDriver at {env_vars['chromedriver_path']} is not executable")
        try:
            os.chmod(env_vars['chromedriver_path'], 0o755)
            logging.info("Fixed ChromeDriver permissions")
        except Exception as e:
            logging.error(f"Failed to fix ChromeDriver permissions: {e}")
            return []
    
    chrome_options = get_chrome_options(env_vars['chrome_binary'])
    
    try:
        logging.info(f"Using ChromeDriver at: {env_vars['chromedriver_path']}")
        service = Service(
            executable_path=env_vars['chromedriver_path'],
            log_path='/tmp/chromedriver.log'
        )

        # Create a new WebDriver instance without using Selenium Manager
        os.environ['webdriver.chrome.driver'] = env_vars['chromedriver_path']
        
        driver = webdriver.Chrome(
            service=service,
            options=chrome_options
        )
        
        logging.info("Chrome driver initialized successfully")
        
        # Test if the driver is working
        logging.info("Testing driver with simple command...")
        driver.get("about:blank")
        logging.info("Driver test successful")
        
        driver.implicitly_wait(10)
        logging.info(f"Fetching data from {url}")
        
        driver.get(url)
        logging.info("Page loaded, waiting for content")
        
        # Wait for table to load
        try:
            wait = WebDriverWait(driver, 10)
            calendar_table = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "calendar__table"))
            )
            logging.info("Calendar table found on page")
        except Exception as e:
            logging.error(f"Timeout waiting for calendar table: {e}")
            if driver.page_source:
                logging.info(f"Page source preview: {driver.page_source[:500]}")
        
        page_source = driver.page_source
        logging.info(f"Page source length: {len(page_source)}")
        
        driver.quit()
        logging.info("Browser closed")
        
        soup = BeautifulSoup(page_source, 'html.parser')
        logging.info("BeautifulSoup object created")
        
        calendar_table = soup.find('table', class_='calendar__table')
        if not calendar_table:
            logging.error("Calendar table not found in parsed HTML")
            logging.info(f"Page source sample: {page_source[:500]}...")
            return []

        events = []
        rows = soup.select('tr.calendar_row, tr.calendar__row')
        logging.info(f"Found {len(rows)} calendar rows")

        if len(rows) == 0:
            all_rows = soup.find_all('tr')
            logging.info(f"Total tr elements found: {len(all_rows)}")
            for i, row in enumerate(all_rows[:5]):
                logging.info(f"Row {i} classes: {row.get('class', 'no class')}")

        current_date = None

        for row in rows:
            try:
                date_elem = row.find('td', class_='date') or row.find('td', class_='calendar__date')
                if date_elem and date_elem.text.strip():
                    current_date = date_elem.text.strip()
                    logging.info(f"Found new date: {current_date}")

                time_elem = row.find(['td', 'time'], class_=['calendar__time', 'time'])
                currency_elem = row.find(['td', 'currency'], class_=['calendar__currency', 'currency'])
                event_elem = row.find(['td', 'event'], class_=['calendar__event', 'event'])

                if all([time_elem, currency_elem, event_elem]):
                    time_text = time_elem.text.strip()
                    currency = currency_elem.text.strip().upper()
                    event = event_elem.text.strip()

                    if currency not in ["USD", "ALL"]:
                        continue
                    
                    event_data = {
                        "date": current_date if current_date else "",
                        "time": time_text if time_text else "All Day",
                        "currency": currency,
                        "event": event
                    }
                    
                    logging.info(f"Adding event: {event_data}")
                    events.append(event_data)

            except Exception as e:
                logging.error(f"Error processing row: {str(e)}")
                logging.error(traceback.format_exc())
                continue

        logging.info(f"Total events scraped: {len(events)}")
        if events:
            logging.info(f"Sample events: {events[:2]}")
        
        return events

    except Exception as e:
        logging.error(f"Error scraping calendar: {str(e)}")
        logging.error(traceback.format_exc())
        if 'driver' in locals():
            driver.quit()
        return []

if __name__ == '__main__':
    scrape_forex_factory_calendar()