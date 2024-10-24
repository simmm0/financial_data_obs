import requests
import logging
from datetime import datetime
from bs4 import BeautifulSoup
import time
import random

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def get_random_user_agent():
    """Return a random modern user agent"""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/115.0.1901.188'
    ]
    return random.choice(user_agents)

def get_json_export_url():
    """Get the current JSON export URL from the calendar page"""
    calendar_url = "https://www.forexfactory.com/calendar"
    
    try:
        headers = {
            'User-Agent': get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://www.forexfactory.com/'
        }
        
        response = requests.get(calendar_url, headers=headers, timeout=10)
        if response.status_code != 200:
            logging.error(f"Failed to get calendar page. Status code: {response.status_code}")
            logging.error(f"Response content: {response.text[:500]}")
            return None
            
        logging.info("Retrieved calendar page")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find link containing the specific URL pattern
        json_link = soup.find('a', href=lambda x: x and 'https://nfs.faireconomy.media/ff_calendar_thisweek.json' in x)
        
        if json_link:
            json_url = json_link.get('href')
            logging.info(f"Found JSON URL: {json_url}")
            return json_url
        else:
            # If not found, try searching for partial matches
            all_links = soup.find_all('a', href=True)
            for link in all_links:
                href = link.get('href', '')
                if 'nfs.faireconomy.media' in href and 'ff_calendar_thisweek.json' in href:
                    logging.info(f"Found JSON URL through partial match: {href}")
                    return href
                    
            logging.error("Could not find JSON export URL")
            logging.debug("Available links:")
            for link in all_links[:10]:  # Log first 10 links for debugging
                logging.debug(f"Link: {link.get('href', '')}")
            return None
            
    except Exception as e:
        logging.error(f"Error getting JSON export URL: {e}")
        logging.error("Response content:", response.text[:500] if 'response' in locals() else "No response")
        return None

def scrape_forex_factory_calendar():
    """Fetch calendar data using current JSON export URL"""
    logging.info("Starting calendar data fetch")
    
    # Try to get URL from the calendar page first
    json_url = get_json_export_url()
    
    if not json_url:
        # If we couldn't get the URL from the page, construct it using current timestamp
        timestamp = int(time.time())
        json_url = f"https://nfs.faireconomy.media/ff_calendar_thisweek.json?version={timestamp}"
        logging.info(f"Using constructed URL: {json_url}")

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