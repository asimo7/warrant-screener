
# import requests
# from flask import Flask, jsonify
# from flask_socketio import SocketIO
# import time
# import random
# import requests
# from flask_cors import CORS
# from collections import defaultdict

# app = Flask(__name__)
# CORS(app, origins=["http://localhost:3000"], supports_credentials=True)
# socketio = SocketIO(app, cors_allowed_origins="http://localhost:3000")

# # Alpha Vantage API configuration
# def get_stocks():
#     BASE_URL = 'http://api.marketstack.com/v1/'

#     # Endpoint for tickers
#     endpoint = 'tickers'

#     # Query parameters
#     params = {
#         'access_key': '706c027847f6cfcb7e008cd7c98994bf',
#         'exchange': 'XNAS',  # Malaysian exchange code
#         'limit': 3       # Adjust limit as needed
#     }

#     # Make the API request
#     response = requests.get(BASE_URL + endpoint, params=params)

#     if response.status_code == 200:
#         print(response)
#         data = response.json()
#         tickers = data.get('data', [])
#         return tickers
#     else:
#         print(f"Error: {response.status_code}, {response.text}")

# def get_warrant_data(symbols):
#     BASE_URL = "https://api.marketstack.com/v1/intraday"
#     access_key = "706c027847f6cfcb7e008cd7c98994bf"
#     processed_batch = []
    
#     # Join symbols with commas for the batch request
#     chosen = ",".join(symbols)
#     querystring = {"access_key": access_key, "symbols": chosen, "interval": "15min"}
    
#     # Fetch the data
#     response = requests.get(BASE_URL, params=querystring)
#     api_data = response.json()
#     print(api_data)
#     if 'data' not in api_data:
#         print("No data found in the response.")
#         return []

#     # Dictionary to store the latest data for each symbol
#     latest_data = defaultdict(lambda: None)
#     last_close = defaultdict(lambda: None)  # Dictionary to store the last valid close value

#     # Iterate over the returned data
#     for entry in api_data['data']:
#         symbol = entry['symbol']
        
#         # If the 'close' value is missing, use the last valid close
#         close_price = entry.get('close', None)
#         if close_price is None:
#             close_price = last_close[symbol]  # Use the last valid close price
        
#         if close_price is not None:
#             open_price = float(entry['open'])
#             high_price = float(entry['high'])
#             low_price = float(entry['low'])
#             vol = int(entry['volume'])
#             change = round(close_price - open_price, 2)
#             percent_change = round((change / open_price) * 100, 5)
#             vwap = round(((open_price + high_price + low_price + close_price) / 4) / vol, 5)
#             turnover = round(vwap * vol, 5)

#             # Store the current close as the last valid close
#             last_close[symbol] = close_price
            
#             # Store the data entry
#             current_entry = {
#                 "date": entry["date"],
#                 "symbol": symbol,
#                 "price": close_price,
#                 "change": change,
#                 "percent_change": percent_change,
#                 "volume": vol,
#                 "VWAP": vwap,
#                 'TO': turnover
#             }

#             # Update the latest data for the symbol if this entry is the latest
#             if latest_data[symbol] is None or current_entry['date'] > latest_data[symbol]['date']:
#                 latest_data[symbol] = current_entry

#     # Add the most recent data for each symbol to the processed_batch
#     processed_batch = list(latest_data.values())

#     return processed_batch

# @socketio.on('connect')
# def handle_connection():
#     print("Client connected!")

# @socketio.on('disconnect')
# def handle_disconnection():
#     print("Client disconnected!")

# def fetch_data():
#     tickers = get_stocks()
#     print(tickers)
#     symbols = [ticker["symbol"] for ticker in tickers[:3]] 
#     print(symbols)
#     while True:
#         data = get_warrant_data(symbols)  # Fetch real-time data
#         print("Fetched data:", data)  # Debug print to verify data fetching
#         socketio.emit('warrant_update', data)  # Send data to frontend
#         print("Emitted data to frontend")  # Debug print to verify emitting
#         time.sleep(60)

# if __name__ == '__main__':
#     socketio.start_background_task(fetch_data)  # Run fetch_data in the background
#     socketio.run(app, host='0.0.0.0', port=5000)





import requests
from flask import Flask, jsonify
from flask_socketio import SocketIO
import time
import random
import requests
from flask_cors import CORS
from collections import defaultdict
from datetime import datetime, timezone
import json
import pandas as pd

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"], supports_credentials=True)
socketio = SocketIO(app, cors_allowed_origins="http://localhost:3000")

# Alpha Vantage API configuration
def get_stocks():
    stocks_elements = pd.read_excel('myr_data.xlsx')
    stocks_elements['Code'] = stocks_elements['Code'].astype(str) + ".KLSE"
    symbol_list = stocks_elements['Code'].tolist()
    name_list = stocks_elements['Name'].tolist()
    return symbol_list[:2], name_list[:2]

def get_warrant_data(symbols,name):
    access_key = "67413dc0158284.44313462"
    BASE_URL = "https://eodhistoricaldata.com/api/real-time/"
    processed_batch = []
    
    latest_data = defaultdict(lambda: None)
    
    # Join the list of symbols into a comma-separated string, excluding the reference_symbol
    symbols_str = ",".join(symbols[1:])
    # Construct the URL for the batch request with 's' as the query parameter and 'AAPL.US' as the reference symbol
    url = f'{BASE_URL}{symbols[0]}?s={symbols_str}&api_token={access_key}&fmt=json'
    
    # Make the request
    response = requests.get(url)

    api_data = response.json()
    print(api_data)

    # Dictionary to store the latest data for each symbol
    latest_data = defaultdict(lambda: None)
    last_close = defaultdict(lambda: None)  # Dictionary to store the last valid close value
    counter = 0
    # Iterate over the returned data
    for entry in api_data:
        symbol = entry['code']
        nama = name[counter]
        counter += 1
        # If the 'close' value is missing, use the last valid close
        close_price = entry.get('close', None)
        if close_price is None:
            close_price = last_close[symbol]  # Use the last valid close price
        
        if close_price is not None:
            timestamp = int(entry['timestamp'])  # Ensure it's an integer
            date = datetime.fromtimestamp(timestamp, timezone.utc)
            formatted_date = date.strftime('%Y-%m-%d %H:%M:%S')
            open_price = float(entry['open'])
            high_price = float(entry['high'])
            low_price = float(entry['low'])
            vol = int(entry['volume'])
            change = round(entry['change'], 2)
            percent_change = round(entry['change_p'], 2)
            vwap = round(((open_price + high_price + low_price + close_price) / 4) / vol, 5)
            turnover = round(vwap * vol, 5)

            # Store the current close as the last valid close
            last_close[symbol] = close_price
            
            # Store the data entry
            current_entry = {
                "date": formatted_date,
                "symbol": symbol,
                "name": nama,
                "price": close_price,
                "change": change,
                "percent_change": percent_change,
                "volume": vol,
                "VWAP": vwap,
                'TO': turnover
            }

            # Update the latest data for the symbol if this entry is the latest
            if latest_data[symbol] is None or current_entry['timestamp'] > latest_data[symbol]['timestamp']:
                latest_data[symbol] = current_entry

    # Add the most recent data for each symbol to the processed_batch
    processed_batch = list(latest_data.values())

    return processed_batch

@socketio.on('connect')
def handle_connection():
    print("Client connected!")

@socketio.on('disconnect')
def handle_disconnection():
    print("Client disconnected!")

def fetch_data():
    tickers, names = get_stocks()
    print(tickers)
    symbols = [ticker for ticker in tickers] 
    desc = [name for name in names] 
    while True:
        data = get_warrant_data(symbols,desc)  # Fetch real-time data
        print("Fetched data:", data)  # Debug print to verify data fetching
        socketio.emit('warrant_update', data)  # Send data to frontend
        print("Emitted data to frontend")  # Debug print to verify emitting
        time.sleep(60)

if __name__ == '__main__':
    socketio.start_background_task(fetch_data)  # Run fetch_data in the background
    socketio.run(app, host='0.0.0.0', port=5000)