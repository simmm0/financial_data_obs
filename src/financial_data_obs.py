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
    chrome_dir = "/opt/render/project/.chrome"  # Use absolute path
    
    env_vars = {
        'chrome_binary': os.getenv('CHROME_BIN', os.path.join(chrome_dir, 'chrome-linux/opt/google/chrome/chrome')),
        'chromedriver_path': os.getenv('CHROMEDRIVER_PATH', os.path.join(chrome_dir, 'chromedriver')),
        'python_path': os.getenv('PYTHONPATH', '/opt/render/project/src'),
        'is_render': os.getenv('RENDER', 'false').lower() == 'true'
    }
    
    # Print debug information
    logging.info(f"Current directory: {os.getcwd()}")
    logging.info(f"Directory exists check - Chrome dir: {os.path.exists(chrome_dir)}")
    logging.info(f"Directory exists check - ChromeDriver: {os.path.exists(env_vars['chromedriver_path'])}")
    
    # Check if ChromeDriver exists and is executable
    if not os.path.exists(env_vars['chromedriver_path']):
        logging.error(f"ChromeDriver not found at {env_vars['chromedriver_path']}")
        # List parent directory contents
        parent_dir = os.path.dirname(env_vars['chromedriver_path'])
        try:
            logging.info(f"Contents of {parent_dir}:")
            logging.info(os.listdir(parent_dir))
        except Exception as e:
            logging.error(f"Could not list parent directory: {e}")
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
    
    return env_vars

def scrape_with_retry(url, max_retries=3, timeout=60):
    """Attempt to scrape with retries and better error handling"""
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            logging.info(f"Scraping attempt {attempt + 1} of {max_retries}")
            
            driver = None
            try:
                env_vars = get_env_vars()
                chrome_options = get_chrome_options(env_vars['chrome_binary'])
                service = Service(
                    executable_path=env_vars['chromedriver_path'],
                    log_path='/tmp/chromedriver.log'
                )
                
                driver = webdriver.Chrome(service=service, options=chrome_options)
                driver.set_page_load_timeout(timeout)
                logging.info("Chrome driver initialized successfully")
                
                # Load the page
                driver.get(url)
                logging.info("Page loaded successfully")
                
                # Wait for calendar table with timeout
                wait = WebDriverWait(driver, 30)
                calendar_table = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".calendar__table, .calendar_table"))
                )
                logging.info("Calendar table found")
                
                # Get page source
                page_source = driver.page_source
                logging.info(f"Retrieved page source, length: {len(page_source)}")
                
                return page_source
                
            except Exception as e:
                last_exception = e
                logging.error(f"Error during attempt {attempt + 1}: {str(e)}")
                continue
            finally:
                if driver:
                    driver.quit()
                    logging.info("Browser closed")
                    
        except Exception as e:
            last_exception = e
            logging.error(f"Outer error during attempt {attempt + 1}: {str(e)}")
            continue
            
    raise last_exception

def scrape_forex_factory_calendar():
    url = "https://www.forexfactory.com/calendar"
    
    logging.info("Starting scrape_forex_factory_calendar function")
    
    try:
        # Get page source with retry logic
        page_source = scrape_with_retry(url)
        
        # Parse the content
        soup = BeautifulSoup(page_source, 'html.parser')
        logging.info("Created BeautifulSoup object")
        
        # Try both possible class names for the calendar table
        calendar_table = soup.find('table', class_=['calendar__table', 'calendar_table'])
        if not calendar_table:
            logging.error("Calendar table not found in parsed HTML")
            all_tables = soup.find_all('table')
            logging.info(f"Found {len(all_tables)} tables on the page")
            for i, table in enumerate(all_tables):
                logging.info(f"Table {i} classes: {table.get('class', 'no class')}")
            return []

        rows = soup.select('tr.calendar_row, tr.calendar__row')
        logging.info(f"Found {len(rows)} calendar rows")

        if len(rows) == 0:
            all_rows = soup.find_all('tr')
            logging.info(f"Total tr elements found: {len(all_rows)}")
            for i, row in enumerate(all_rows[:5]):
                logging.info(f"Row {i} classes: {row.get('class', 'no class')}")
                logging.info(f"Row {i} content: {row.text.strip()}")

        events = []
        current_date = None

        for row in rows:
            try:
                date_elem = row.find('td', class_='date') or row.find('td', class_='calendar__date')
                if date_elem and date_elem.text.strip():
                    current_date = date_elem.text.strip()
                    logging.info(f"Found date: {current_date}")

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

        logging.info(f"Total events found: {len(events)}")
        if events:
            logging.info(f"First few events: {events[:2]}")
        else:
            logging.warning("No events were found in the scraped data")
            
        return events

    except Exception as e:
        logging.error(f"Error in main scraping function: {str(e)}")
        logging.error(traceback.format_exc())
        return []

if __name__ == '__main__':
    scrape_forex_factory_calendar()