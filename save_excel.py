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

endpoint = "https://eodhd.com/api/exchange-symbol-list/KLSE?api_token=67413dc0158284.44313462&fmt=json"
response = requests.get(endpoint)
exchange_stocks = response.json()  # Parse JSON response
myr_df = pd.DataFrame(json.loads(response.text))
output_file = "myr_data.xlsx"  # Specify the desired file name
myr_df.to_excel(output_file, index=False)