import sys
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
from flask import Flask, render_template_string

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

def scrape_forex_factory_calendar():
    url = "https://www.forexfactory.com/calendar"
    # headers = {
    #    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    #    'Accept-Language': 'en-US,en;q=0.9',
    #}
    
    # Setup headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Specify the path to Chromium
    chrome_options.binary_location = "/usr/bin/chromium-browser"

    # Setup Chrome WebDriver using ChromeDriverManager
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        logging.info(f"Fetching data from {url}")
        driver.get(url)

        # Wait for the page to load (adjust time if needed)
        driver.implicitly_wait(10)
        
        # Use BeautifulSoup to parse the page source
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        logging.info(f"BeautifulSoup object created")
        
        # Close the Selenium driver
        driver.quit()

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
        driver.quit()
        return []

@app.route('/')
def index():
    try:
        logging.info("Starting to fetch data")
        calendar = scrape_forex_factory_calendar()
        logging.info(f"Fetched {len(calendar)} calendar events")
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logging.info("Finished fetching data")
        
        html = """
        <html>
        <head>
            <title>Economic Calendar</title>
            <style>
                body { 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background-color: #f0f4f8;
                    color: #1e3a5f;
                    margin: 0; 
                    padding: 10px;
                    font-size: 13px;
                }
                .container { 
                    max-width: 800px; 
                    margin: 0 auto;
                    background: #f0f4f8;
                    padding: 15px;
                    border-radius: 10px;
                    box-shadow: 8px 8px 16px #d1d9e6,
                            -8px -8px 16px #ffffff;
                }
                h1 { 
                    color: #1e3a5f;
                    padding-bottom: 8px;
                    margin: 0 0 10px 0;
                    font-weight: 600;
                    font-size: 18px;
                }
                table { 
                    width: 100%; 
                    border-collapse: separate;
                    border-spacing: 0;
                    margin-top: 10px;
                    background: #f0f4f8;
                    border-radius: 8px;
                    box-shadow: inset 3px 3px 5px #d1d9e6,
                            inset -3px -3px 5px #ffffff;
                    padding: 8px;
                }
                th, td { 
                    padding: 4px 8px;
                    text-align: left;
                    border-bottom: 1px solid #e0e5ec;
                    font-size: 12px;
                    line-height: 1.2;
                }
                th { 
                    background-color: #f0f4f8;
                    color: #1e3a5f;
                    font-weight: 600;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }
                tr:last-child td {
                    border-bottom: none;
                }
                tr:hover {
                    background-color: rgba(33, 150, 243, 0.05);
                }
                .time-cell { 
                    color: #666;
                    width: 75px;
                }
                .currency-cell { 
                    color: #2196f3;
                    font-weight: 600;
                    width: 60px;
                }
                td:first-child {
                    width: 80px;
                }
                #timer { 
                    font-size: 11px;
                    margin-top: 8px;
                    text-align: right;
                    color: #666;
                    background: #f0f4f8;
                    padding: 4px 8px;
                    border-radius: 5px;
                    display: inline-block;
                    float: right;
                    box-shadow: 2px 2px 4px #d1d9e6,
                            -2px -2px 4px #ffffff;
                }
                .last-updated { 
                    color: #666;
                    font-size: 10px;
                    text-align: right;
                    margin-top: 5px;
                    clear: both;
                }
                tr:nth-child(even) { 
                    background-color: rgba(240, 244, 248, 0.5);
                }
            </style>
            <script>
                function startTimer(duration, display) {
                    var timer = duration, minutes, seconds;
                    setInterval(function () {
                        minutes = parseInt(timer / 60, 10);
                        seconds = parseInt(timer % 60, 10);

                        minutes = minutes < 10 ? "0" + minutes : minutes;
                        seconds = seconds < 10 ? "0" + seconds : seconds;

                        display.textContent = minutes + ":" + seconds;

                        if (--timer < 0) {
                            timer = duration;
                            location.reload();
                        }
                    }, 1000);
                }

                window.onload = function () {
                    var fiveMinutes = 60 * 5,
                        display = document.querySelector('#time');
                    startTimer(fiveMinutes, display);
                };
            </script>
        </head>
        <body>
            <div class="container">
                <h1>Economic Calendar</h1>
                <table>
                    <tr>
                        <th>Date</th>
                        <th>Time</th>
                        <th>Currency</th>
                        <th>Event</th>
                    </tr>
                    {% for event in calendar %}
                    <tr>
                        <td>{{ event.date }}</td>
                        <td class="time-cell">{{ event.time }}</td>
                        <td class="currency-cell">{{ event.currency }}</td>
                        <td>{{ event.event }}</td>
                    </tr>
                    {% endfor %}
                </table>
                {% if not calendar %}
                <p>No upcoming events found.</p>
                {% endif %}
                <div id="timer">Next update in <span id="time">05:00</span></div>
                <p class="last-updated">Last updated: {{ current_time }}</p>
            </div>
        </body>
        </html>
        """
        return render_template_string(html, calendar=calendar, current_time=current_time)
    except Exception as e:
        logging.error(f"An error occurred in the index route: {str(e)}")
        logging.error(traceback.format_exc())
        return f"An error occurred: {str(e)}", 500

if __name__ == '__main__':
    try:
        logging.info("Starting the Flask application")
        app.run(debug=True)
    except Exception as e:
        logging.error(f"An error occurred while starting the application: {str(e)}")
        logging.error(traceback.format_exc())