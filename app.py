from flask import Flask, render_template, request, flash, redirect, jsonify
import csv, datetime
from binance.client import Client
from binance.enums import *
import keys

crypto_web_app = Flask(__name__)

crypto_web_app.secret_key = "032404"

client = Client(keys.binanace_api_key, keys.binanace_api_secret, tld='us')


@crypto_web_app.route('/')
def index():
    title = 'CryptoWebApp'

    account = client.get_account()

    balances = account['balances']

    exchange_info = client.get_exchange_info()
    symbols = exchange_info['symbols']

    return render_template('index.html', title=title, my_balances=balances, symbols=symbols)


@crypto_web_app.route('/buy', methods=['POST'])
def buy():
    print(request.form)
    try:
        order = client.create_order(symbol=request.form['symbol'],
                                    side=SIDE_BUY,
                                    type=ORDER_TYPE_MARKET,
                                    quantity=request.form['quantity'])
    except Exception as e:
        flash(e.message, "error")

    return redirect('/')


@crypto_web_app.route('/sell')
def sell():
    return 'sell'


@crypto_web_app.route('/settings')
def settings():
    return 'settings'


@crypto_web_app.route('/history')
def history():
    candlesticks = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_1MINUTE, "1 Jan, 2019", "23 May, 2021")

    processed_candlesticks = []

    for data in candlesticks:  # re-write file so that it is readable by chart.js
        candlestick = {
            "time": data[0] / 1000,  # switch to seconds
            "open": data[1],
            "high": data[2],
            "low": data[3],
            "close": data[4]
        }

        processed_candlesticks.append(candlestick)

    return jsonify(processed_candlesticks)  # reformat python as json


if __name__ == "__main__":
    crypto_web_app.run(debug=True)
