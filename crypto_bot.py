"""
Gina McKeown
Advanced Programmer's Workshop

Crypto Trading Bot

This program accesses the prices of a cryptocurrency and uses the RSI (Relative Strength Indicator) to recommend times
to buy and sell. The program sends text reminders, but can also automatically buy and sell cryptocurrency of a certain
amount in USD. It checks all the closing prices of each candlestick, and uses them to measure the RSI, once the RSI is
below 30 or above 70, the program will act according (buying or selling). The program acts through binance, but sends
SMS messages through twilio.

"""


import talib
import numpy as np
import websocket
import json
import pprint
from binance import *
from binance.enums import *
from keys import binanace_api_secret, binanace_api_key

# Messaging
from keys import twilio_api_token, twilio_api_SID
from twilio.rest import Client as Receiver

# CONSTANTS
SOCKET = "wss://stream.binance.com:9443/ws/btcusdt@kline_1m"  # web socket data
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

# Initial Variables
closes = []
ready_to_trade = False

# User specifications
currency = "BTCUSD"
trade_quantity = 0.0

number = "+19292455707"
twilio_phone_num = "+15013652799"

client = Client(binanace_api_secret, binanace_api_key)


def trade(side, quantity, symbol):
    """
    Buys and sells cryptocurrency according to the given parameters. Works through binance.
    :param side: buying ot selling
    :param quantity: amount to buy or sell
    :param symbol: type of currency
    :return: true or false for successful trade
    """
    try:
        print("Sending Order")
        # create an order through binance
        order = client.create_order(symbol=symbol,
                                    side=side,
                                    type=ORDER_TYPE_MARKET,
                                    quantity=quantity)
        print(order)
    except Exception as e:
        print("an exception occured - {}".format(e))
        return False

    return True


def on_open(ws):
    """
    lets user know when connection is open
    :param ws: the web socket app used
    :return: none
    """
    print("Opened Connection")


def on_close(ws):
    """
    lets user know when connection is closed
    :param ws: the web socket app used
    :return: none
    """
    print("Closed Connection")


def on_message(ws, message):
    """
    runs while web socket app is active

    This function buys and sells and sends SMS recommendations based on the RSI of a specific cryptocurrency. All of the
    closing candle numbers are added to a list and then compared to calculate RSI. Orders are only completed once.
    :param ws: the web socket app used
    :param message: the live data in json format
    :return: none
    """
    global currency, ready_to_trade, trade_quantity, number
    json_message = json.loads(message)  # load as json
    # pprint.pprint(json_message) # prints all live data

    candle = json_message["k"]  # candle data
    candle_closed = candle["x"]  # end of candle
    close = candle["c"]  # closing price

    if candle_closed:  # when reaching the end of a candle
        print("Candle closed at {}".format(close))
        closes.append(float(close))  # add new close to list of closes
        print("All closes:")
        print(closes)

        # once enough closes have occurred for viable calculations
        if len(closes) > RSI_PERIOD:
            np_closes = np.array(closes)  # convert array of closes to np array
            rsi = talib.RSI(np_closes, RSI_PERIOD)  # calculated RSI using talib
            print(rsi)
            last_rsi = rsi[-1]
            last_close = closes[-1]
            print("Current RSI is {}".format(last_rsi))

            if last_rsi > RSI_OVERBOUGHT:
                if ready_to_trade:  # in trading position
                    reminder = "Overbought: Sell " + currency + "\nRSI: " + str(last_rsi) + "\nPrice: " + str(last_close)
                    print(reminder)
                    send_sms(number, reminder)  # text reminder
                    order_succeeded = trade(SIDE_SELL, trade_quantity, currency)

                    if order_succeeded:
                        ready_to_trade = False  # sold, nothing left to sell
                else:
                    # prevents continuous selling
                    print("Overbought, but don't own any, nothing to sell")

            if last_rsi < RSI_OVERSOLD:
                if ready_to_trade:
                    # prevents continuous buying
                    print("Oversold, but already purchased. No action. ")
                else:
                    reminder = "Oversold: Buy " + currency + "\nRSI: " + last_rsi + "\nPrice: " + last_close
                    print(reminder)
                    send_sms(number, reminder)  # text reminder
                    order_succeeded = trade(SIDE_BUY, trade_quantity, currency)

                    if order_succeeded:
                        ready_to_trade = True  # bought, don't buy again


def on_error(ws, error):
    """
    If there is an error in the web socket app, print the error
    :param ws: the web socket app used
    :param error: the error
    :return:
    """
    print(error)


def send_sms(number, message):
    """
    This function sends a message to the given recipient. The message contains the given message
    and the recommended clothing for
    :param number: phone number of recipient
    :param message: a string message to send to recipient
    :return: a boolean for whether or not the message sent successfully
    """
    text_recipient = Receiver(twilio_api_SID, twilio_api_token)  # Create an client object
    try:
        text_recipient.api.account.messages.create(
            body=message,
            to=number,  # Destination phone number
            from_=twilio_phone_num
        )

    except:
        print("There was an error sending your message")
        return False
    return True


if __name__ == "__main__":
    ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message, on_error=on_error)
    ws.run_forever()
