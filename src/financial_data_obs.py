import requests
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def scrape_forex_factory_calendar():
    """Fetch calendar data directly from the JSON endpoint"""
    base_url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
    
    logging.info("Starting calendar data fetch")
    
    try:
        # Set up headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.90 Safari/537.36',
            'Accept': 'application/json'
        }

        # Make the request
        logging.info(f"Fetching data from {base_url}")
        response = requests.get(base_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            logging.info("Successfully fetched and parsed JSON data")
            
            events = []
            for event in data:
                # Check if this is a USD or ALL event
                currency = event.get('currency', '').upper()
                if currency not in ["USD", "ALL"]:
                    continue
                
                # Convert timestamp to date string
                try:
                    date_str = event.get('date', '')
                    if date_str:
                        date = datetime.fromtimestamp(int(date_str)).strftime('%b %d')
                    else:
                        date = ''
                except:
                    date = event.get('date', '')
                
                # Extract time, defaulting to "All Day"
                time = event.get('time', 'All Day')
                
                event_data = {
                    "date": date,
                    "time": time,
                    "currency": currency,
                    "event": event.get('title', '')
                }
                
                logging.info(f"Adding event: {event_data}")
                events.append(event_data)
            
            # Sort events by date and time
            def sort_key(event):
                # Convert date string (e.g., "Oct 23") to comparable value
                try:
                    date_obj = datetime.strptime(event['date'], '%b %d')
                    # Handle year transition (December -> January)
                    if date_obj.month < datetime.now().month:
                        date_obj = date_obj.replace(year=datetime.now().year + 1)
                    else:
                        date_obj = date_obj.replace(year=datetime.now().year)
                    
                    # Convert time string to sortable value
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
                    return (datetime.max, 0)  # Put unparseable dates at the end
            
            events.sort(key=sort_key)
            
            logging.info(f"Total events found: {len(events)}")
            if events:
                logging.info(f"First few events: {events[:2]}")
            
            return events
            
        else:
            logging.error(f"Failed to fetch data. Status code: {response.status_code}")
            return []
            
    except Exception as e:
        logging.error(f"Error fetching calendar data: {e}")
        return []

if __name__ == '__main__':
    scrape_forex_factory_calendar()