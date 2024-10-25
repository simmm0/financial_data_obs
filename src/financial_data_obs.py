import requests
import logging
from datetime import datetime
import time
import random
import traceback

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
    """Get JSON URL directly without scraping"""
    base_url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
    timestamp = int(time.time())
    return f"{base_url}?version={timestamp}"

def scrape_forex_factory_calendar():
    """Fetch calendar data using JSON export URL"""
    logging.info("Starting calendar data fetch")
    
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
                logging.info(f"Successfully parsed JSON response with {len(data)} events")
                
                events = []
                for event in data:
                    country = event.get('country', '').upper()
                    if country not in ["USD", "ALL"]:
                        continue
                    
                    try:
                        # Parse the ISO format date string
                        date_str = event.get('date', '')
                        if date_str:
                            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                            date = date_obj.strftime('%b %d')
                            time = date_obj.strftime('%I:%M%p').lstrip('0')  # Remove leading zero
                        else:
                            date = ''
                            time = 'All Day'
                    except Exception as e:
                        logging.error(f"Error parsing date {date_str}: {e}")
                        date = ''
                        time = 'All Day'
                    
                    # Get impact and determine color
                    impact = event.get('impact', '')
                    impact_color = ''
                    if impact.lower() == 'low':
                        impact_color = '#ffd700'  # Yellow
                    elif impact.lower() == 'medium':
                        impact_color = '#ffa500'  # Orange
                    elif impact.lower() == 'high':
                        impact_color = '#ff0000'  # Red
                    
                    event_data = {
                        "date": date,
                        "time": time,
                        "currency": country,
                        "event": event.get('title', ''),
                        "impact": impact,
                        "impact_color": impact_color,
                        "forecast": event.get('forecast', ''),
                        "previous": event.get('previous', '')
                    }
                    
                    logging.debug(f"Adding event: {event_data}")
                    events.append(event_data)
                
                # Sort events
                def sort_key(event):
                    try:
                        time_str = event['time'] if event['time'] != 'All Day' else '00:00AM'
                        date_obj = datetime.strptime(f"{event['date']} {time_str}", '%b %d %I:%M%p')
                        if date_obj.month < datetime.now().month:
                            date_obj = date_obj.replace(year=datetime.now().year + 1)
                        else:
                            date_obj = date_obj.replace(year=datetime.now().year)
                        return date_obj
                    except Exception as e:
                        logging.error(f"Error sorting event {event}: {e}")
                        return datetime.max
                
                events.sort(key=sort_key)
                
                logging.info(f"Total events found: {len(events)}")
                if events:
                    logging.info(f"First few events: {events[:2]}")
                else:
                    logging.warning("No events found after filtering")
                
                return events
                
            except Exception as e:
                logging.error(f"Error processing JSON data: {e}")
                logging.error(traceback.format_exc())
                return []
        else:
            logging.error(f"Failed to fetch data. Status code: {response.status_code}")
            logging.error(f"Response content: {response.text[:500]}")
            return []
            
    except Exception as e:
        logging.error(f"Error in main scraping function: {e}")
        logging.error(traceback.format_exc())
        return []

if __name__ == '__main__':
    scrape_forex_factory_calendar()