from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from src.financial_data_obs import scrape_forex_factory_calendar
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/api/calendar')
def get_calendar():
    calendar = scrape_forex_factory_calendar()
    return jsonify(calendar)

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    app.run(debug=True)