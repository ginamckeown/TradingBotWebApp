"""

"""
from binance.client import Client
import config
import csv

client = Client(config.API_KEY, config.API_SECRET)


csvfile = open('2021_15minutes.csv', 'w', newline='')
candlestick_writer = csv.writer(csvfile, delimiter=',')

candlesticks = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_1MINUTE, "1 Jan, 2017", "23 May, 2021")


for candlestick in candlesticks:
    candlestick[0] = candlestick[0] / 1000
    candlestick_writer.writerow(candlestick)

csvfile.close()

print(candlestick)
