from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from src.financial_data_obs import scrape_forex_factory_calendar
import os
import logging

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/api/calendar')
def get_calendar():
    logging.info("API endpoint /api/calendar called")
    calendar = scrape_forex_factory_calendar()
    logging.info(f"Returning {len(calendar)} events")
    return jsonify(calendar)

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)