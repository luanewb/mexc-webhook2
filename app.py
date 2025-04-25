from flask import Flask, request, jsonify
import os
import time
import hmac
import hashlib
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("MEXC_API_KEY")
SECRET_KEY = os.getenv("MEXC_SECRET_KEY")
BASE_URL = "https://api.mexc.com"

def create_signature(query_string):
    return hmac.new(SECRET_KEY.encode(), query_string.encode(), hashlib.sha256).hexdigest()

def place_order(symbol, side, quantity, price):
    path = '/api/v3/order'
    timestamp = int(time.time() * 1000)

    params = {
        'symbol': symbol,
        'side': side,
        'type': 'LIMIT',
        'quantity': quantity,
        'price': price,
        'recvWindow': 5000,
        'timestamp': timestamp
    }

    query_string = '&'.join(f"{k}={v}" for k, v in params.items())
    signature = create_signature(query_string)
    params['signature'] = signature

    headers = {
        'X-MEXC-APIKEY': API_KEY
    }

    response = requests.post(BASE_URL + path, headers=headers, params=params)
    return response.json()

@app.route('/')
def home():
    return '✅ Webhook MEXC đang chạy', 200

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    print("📩 Webhook nhận được:", data)

    try:
        symbol = data['symbol']
        side = data['action'].upper()
        quantity = float(data['quantity'])
        price = float(data['price'])

        order_response = place_order(symbol, side, quantity, price)
        return jsonify({'status': 'success', 'order_response': order_response}), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

if __name__ == '__main__':
    app.run(port=5000)
