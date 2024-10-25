import requests
import logging
from datetime import datetime
from bs4 import BeautifulSoup
import time  # Make sure this is at the top level
import random

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def get_random_user_agent():
    """Return a random modern user agent"""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/115.0.1901.188',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0'
    ]
    return random.choice(user_agents)

def get_json_url_direct():
    """Get JSON URL directly without scraping the page"""
    base_url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
    timestamp = int(time.time())  # Now time is properly in scope
    return f"{base_url}?version={timestamp}"

def scrape_forex_factory_calendar():
    """Fetch calendar data using JSON export URL"""
    logging.info("Starting calendar data fetch")
    
    # Get the JSON URL directly instead of scraping
    json_url = get_json_url_direct()
    logging.info(f"Using URL: {json_url}")

    try:
        headers = {
            'User-Agent': get_random_user_agent(),
            'Accept': 'application/json',
            'Referer': 'https://www.forexfactory.com/calendar',
            'Origin': 'https://www.forexfactory.com',
            'Host': 'nfs.faireconomy.media'
        }

        logging.info(f"Fetching data from {json_url}")
        response = requests.get(json_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            try:
                data = response.json()
                logging.info(f"Successfully parsed JSON response")
                
                events = []
                for event in data:
                    currency = event.get('currency', '').upper()
                    if currency not in ["USD", "ALL"]:
                        continue
                    
                    try:
                        date_str = event.get('date', '')
                        if date_str:
                            date = datetime.fromtimestamp(int(date_str)).strftime('%b %d')
                        else:
                            date = ''
                    except:
                        date = event.get('date', '')
                    
                    time = event.get('time', 'All Day')
                    
                    event_data = {
                        "date": date,
                        "time": time,
                        "currency": currency,
                        "event": event.get('title', '')
                    }
                    
                    logging.debug(f"Adding event: {event_data}")
                    events.append(event_data)
                
                # Sort events
                def sort_key(event):
                    try:
                        date_obj = datetime.strptime(event['date'], '%b %d')
                        if date_obj.month < datetime.now().month:
                            date_obj = date_obj.replace(year=datetime.now().year + 1)
                        else:
                            date_obj = date_obj.replace(year=datetime.now().year)
                        
                        time_str = event['time']
                        if time_str == 'All Day':
                            time_value = 0
                        else:
                            try:
                                time_obj = datetime.strptime(time_str, '%I:%M%p')
                                time_value = time_obj.hour * 60 + time_obj.minute
                            except:
                                time_value = 0
                        
                        return (date_obj, time_value)
                    except:
                        return (datetime.max, 0)
                
                events.sort(key=sort_key)
                
                logging.info(f"Total events found: {len(events)}")
                if events:
                    logging.info(f"First few events: {events[:2]}")
                
                return events
                
            except Exception as e:
                logging.error(f"Error processing JSON data: {e}")
                return []
        else:
            logging.error(f"Failed to fetch data. Status code: {response.status_code}")
            logging.error(f"Response content: {response.text[:500]}")
            return []
            
    except Exception as e:
        logging.error(f"Error in main scraping function: {e}")
        return []

if __name__ == '__main__':
    scrape_forex_factory_calendar()