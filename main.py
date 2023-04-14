import yfinance as yf
import json

ticker = yf.Ticker("AAPL")
json_formatted_str = json.dumps(ticker.info, indent=2)
print(json_formatted_str)
