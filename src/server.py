# server.py

from datetime import datetime
from flask import Flask, request, jsonify
import re
import os
from functions import get_news_data_av, get_top_gainers_losers_av, get_news_data_n, company_to_ticker, ticker_to_company

# Initialize Flask app
SERVER_ADDRESS = os.getenv("FLASK_RUN_HOST", "127.0.0.1")
PORT = int(os.getenv("FLASK_RUN_PORT", 5000))  # Default to 5000 if not set

app = Flask(__name__)


@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Data Collection API!"}), 200


@app.route("/status")
def get_status():
    return jsonify({"status": "Server is running", "port": PORT}), 200
# Route to get news sentiment data from Alpha Vantage


@app.route('/news_alpha_vantage', methods=['GET'])
def news_alpha_vantage():
    tickers = request.args.get('tickers')
    time_from = request.args.get('time_from')
    time_to = request.args.get('time_to')
    sort = request.args.get('sort', 'LATEST')
    limit = request.args.get('limit', 10)

    data = get_news_data_av(
        tickers=tickers, time_from=time_from, time_to=time_to, sort=sort, limit=limit)
    return jsonify(data)

# Route to get top gainers and losers from Alpha Vantage


@app.route('/top_gainers_losers', methods=['GET'])
def top_gainers_losers():
    data = get_top_gainers_losers_av()
    return jsonify(data)

# Route to get news data from News API


@app.route('/newsapi', methods=['GET'])
def newsapi():
    name = request.args.get('name')
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    print(f"DEBUG: name: {name} from: {from_date} to: {to_date}")
    if not name or not re.match(r'^[a-zA-Z\s]+$', name) or re.search(r'\b(AND|OR|NOT)\b', name, re.IGNORECASE):
        return jsonify({"error": "Invalid 'name' given"}), 400
    if from_date and not to_date or to_date and not from_date:
        return jsonify({"error": "Please provide both to and from dates or none"}), 400
    if from_date and to_date:
        try:
            datetime.fromisoformat(from_date)
            datetime.fromisoformat(to_date)
        except ValueError:
            return jsonify({"error": "Date values must be of ISO 8601 format (e.g. 2025-03-04 or 2025-03-04T07:11:59)"}), 400
    data = get_news_data_n(name=name, from_date=from_date, to_date=to_date)
    return jsonify(data)


@app.route('/convert/company_to_ticker')
def convert_company_to_ticker():
    name = request.args.get('name')

    if not name or not re.match(r'^[a-zA-Z\s]+$', name):
        return jsonify({"error": "Invalid 'name' given"}), 400
    
    data = company_to_ticker(name=name)
    return jsonify(data)


@app.route('/convert/ticker_to_company')
def convert_ticker_to_company():
    ticker = request.args.get('ticker')
    full_name = request.args.get('fullname')

    if not ticker:
        return jsonify({"error": "Invalid 'name' given"}), 400
    
    if not full_name:
        full_name = False
    elif full_name.strip().lower() == 'true':
        full_name = True
    else:
        full_name = False
    
    data = ticker_to_company(ticker=ticker, full_name=full_name)
    return jsonify(data)


# Run the Flask app
if __name__ == '__main__':
    app.run(host=SERVER_ADDRESS, port=PORT, debug=False)
