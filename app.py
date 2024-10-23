from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from src.financial_data_obs import scrape_forex_factory_calendar
import os
import logging
from functools import wraps
from time import time

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def timing_decorator(f):
    @wraps(f)
    def wrap(*args, **kw):
        ts = time()
        try:
            result = f(*args, **kw)
        except Exception as e:
            logging.error(f"Error in {f.__name__}: {str(e)}")
            return jsonify({'error': 'Internal server error', 'message': str(e)}), 500
        finally:
            te = time()
            logging.info(f'Function: {f.__name__}, Time: {te-ts:2.4f} sec')
        return result
    return wrap

@app.route('/api/calendar')
@timing_decorator
def get_calendar():
    logging.info("API endpoint /api/calendar called")
    try:
        calendar = scrape_forex_factory_calendar()
        if not calendar:
            return jsonify({'error': 'No data available', 'message': 'Failed to fetch calendar data'}), 404
        logging.info(f"Returning {len(calendar)} events")
        return jsonify(calendar)
    except Exception as e:
        logging.error(f"Error in get_calendar: {str(e)}")
        return jsonify({'error': 'Server error', 'message': str(e)}), 500

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)