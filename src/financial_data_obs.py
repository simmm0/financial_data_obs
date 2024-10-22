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

def get_env_vars():
    """Get environment variables with proper checks"""
    env_vars = {
        'chrome_binary': os.getenv('CHROME_BIN', '/usr/bin/google-chrome'),
        'chromedriver_path': os.getenv('CHROMEDRIVER_PATH', '/usr/local/bin/chromedriver'),
        'python_path': os.getenv('PYTHONPATH', '/opt/render/project/src'),
        'is_render': os.getenv('RENDER', 'false').lower() == 'true'
    }
    logging.info(f"Environment variables: {env_vars}")
    return env_vars

def scrape_forex_factory_calendar():
    url = "https://www.forexfactory.com/calendar"
    
    logging.info("Starting scrape_forex_factory_calendar function")
    env_vars = get_env_vars()
    logging.info(f"Current working directory: {os.getcwd()}")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.90 Safari/537.36')

    if env_vars['is_render']:
        # Try both Chrome and Chromium paths
        chrome_paths = [
            '/usr/bin/google-chrome',
            '/usr/bin/chromium',
            '/usr/bin/chromium-browser'
        ]
        chromedriver_paths = [
            '/usr/local/bin/chromedriver',
            '/usr/bin/chromedriver'
        ]
        
        # Find the first available Chrome binary
        for chrome_path in chrome_paths:
            if os.path.exists(chrome_path):
                chrome_options.binary_location = chrome_path
                logging.info(f"Using Chrome binary: {chrome_path}")
                break
        else:
            logging.error("No Chrome binary found in any expected location")
        
        # Find the first available ChromeDriver
        for driver_path in chromedriver_paths:
            if os.path.exists(driver_path):
                service = Service(executable_path=driver_path)
                logging.info(f"Using ChromeDriver path: {driver_path}")
                break
        else:
            logging.error("No ChromeDriver found in any expected location")
            service = Service(executable_path=env_vars['chromedriver_path'])
    else:
        service = Service(executable_path="chromedriver")

    try:
        logging.info("Initializing Chrome driver")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        logging.info("Chrome driver initialized successfully")
        
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