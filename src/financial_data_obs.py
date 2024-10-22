import sys
import os
import traceback
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def scrape_forex_factory_calendar():
    url = "https://www.forexfactory.com/calendar"
    
    logging.info("Starting scrape_forex_factory_calendar function")
    logging.info(f"RENDER environment variable: {'RENDER' in os.environ}")
    logging.info(f"Current working directory: {os.getcwd()}")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')

    try:
        if "RENDER" in os.environ:
            # Running on Render
            logging.info("Checking Chromium and ChromeDriver installation:")
            logging.info(f"Chromium exists: {os.path.exists('/usr/bin/chromium-browser')}")
            logging.info(f"ChromeDriver exists: {os.path.exists('/opt/chromedriver/chromedriver')}")
            
            chrome_options.binary_location = "/usr/bin/chromium-browser"
            service = Service(executable_path="/opt/chromedriver/chromedriver")
        else:
            # Running locally
            service = Service(ChromeDriverManager().install())

        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.implicitly_wait(10)  # Add implicit wait
        
        logging.info(f"Fetching data from {url}")
        driver.get(url)
        time.sleep(5)  # Wait for JavaScript to load
        
        # Get the page source after JavaScript has loaded
        page_source = driver.page_source
        
        # Close the browser
        driver.quit()
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(page_source, 'html.parser')
        logging.info(f"BeautifulSoup object created")
        
        # Parse the calendar table
        calendar_table = soup.find('table', class_='calendar__table')
        if not calendar_table:
            logging.error("Calendar table not found")
            return []

        events = []
        rows = soup.select('tr.calendar_row, tr.calendar__row')
        logging.info(f"Found {len(rows)} calendar rows")

        current_date = None

        for row in rows:
            try:
                # Try to find the date in this row
                date_elem = row.find('td', class_='date') or row.find('td', class_='calendar__date')
                
                if date_elem and date_elem.text.strip():
                    current_date = date_elem.text.strip()
                    logging.info(f"Found new date: {current_date}")

                # Get time and event details
                time_elem = row.find(['td', 'time'], class_=['calendar__time', 'time'])
                currency_elem = row.find(['td', 'currency'], class_=['calendar__currency', 'currency'])
                event_elem = row.find(['td', 'event'], class_=['calendar__event', 'event'])

                if all([time_elem, currency_elem, event_elem]):
                    time_text = time_elem.text.strip()
                    currency = currency_elem.text.strip().upper()
                    event = event_elem.text.strip()

                    # Filter USD and ALL events
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
        return events

    except Exception as e:
        logging.error(f"Error scraping calendar: {str(e)}")
        logging.error(traceback.format_exc())
        if 'driver' in locals():
            driver.quit()
        return []