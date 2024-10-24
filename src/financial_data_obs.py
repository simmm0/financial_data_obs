import requests
import logging
from datetime import datetime
import time
import random
import json
import brotli  # For decompressing the response

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def get_random_user_agent():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/115.0.1901.188'
    ]
    return random.choice(user_agents)

def fetch_with_retry(url, max_retries=3, initial_delay=1):
    headers = {
        'User-Agent': get_random_user_agent(),
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://www.forexfactory.com/',
        'Origin': 'https://www.forexfactory.com'
    }

    for attempt in range(max_retries):
        try:
            if attempt > 0:
                delay = initial_delay * (2 ** (attempt - 1)) + random.uniform(0, 1)
                logging.info(f"Retry attempt {attempt + 1}, waiting {delay:.2f} seconds")
                time.sleep(delay)

            response = requests.get(url, headers=headers, timeout=10)
            
            logging.info(f"Response status code: {response.status_code}")
            logging.info(f"Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                content_encoding = response.headers.get('Content-Encoding', '').lower()
                try:
                    if content_encoding == 'br':
                        # Decompress brotli-encoded content
                        raw_content = brotli.decompress(response.content)
                        content = raw_content.decode('utf-8')
                    else:
                        content = response.text

                    logging.info(f"Response content (first 500 chars): {content[:500]}")
                    return content
                except Exception as e:
                    logging.error(f"Error decoding content: {e}")
                    return None
            elif response.status_code == 429:
                logging.warning(f"Rate limited on attempt {attempt + 1}")
                retry_after = response.headers.get('Retry-After')
                if retry_after:
                    time.sleep(int(retry_after))
                continue
            else:
                logging.error(f"Failed with status code: {response.status_code}")
                return None

        except requests.RequestException as e:
            logging.error(f"Request failed on attempt {attempt + 1}: {e}")
            if attempt == max_retries - 1:
                return None
            continue
    
    return None

def scrape_forex_factory_calendar():
    urls = [
        "https://nfs.faireconomy.media/ff_calendar_thisweek.json",
        "https://nfs.faireconomy.media/ff_calendar_thisweek.json?version=latest"
    ]
    
    logging.info("Starting calendar data fetch")
    
    for url in urls:
        try:
            logging.info(f"Trying URL: {url}")
            content = fetch_with_retry(url)
            if not content:
                logging.error(f"Failed to fetch data from {url}")
                continue

            try:
                data = json.loads(content)
                logging.info(f"Successfully parsed JSON response with {len(data)} events")
            except json.JSONDecodeError as e:
                logging.error(f"JSON decode error: {e}")
                logging.error(f"Raw content: {content[:1000]}")
                continue

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
            
            if events:
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
            logging.error(f"Error processing URL {url}: {e}", exc_info=True)
            continue
    
    logging.error("All URLs failed")
    return []

if __name__ == '__main__':
    scrape_forex_factory_calendar()