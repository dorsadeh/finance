# https://finviz.com/screener.ashx?v=111&f=fa_div_o2&ft=4]

import pandas as pd
import requests

ticker_dict = {}
# Download the list of S&P 500 companies from Wikipedia
url = 'https://en.wikipedia.org/wiki/S%26P_500_Dividend_Aristocrats'
html = requests.get(url).content
df_list = pd.read_html(html)
df = df_list[-1]
dividend_aristocrats_list = df["Ticker symbol"].to_list()
ticker_dict["dividend_aristocrats"] = dividend_aristocrats_list

# Download the list of Chalengers from digin
url = 'https://www.digrin.com/stocks/list/7-challengers/'
html = requests.get(url).content
df_list = pd.read_html(html)
df = df_list[-1]
ticker_and_name_list = df["Stock"].to_list()
challengers = []
for item in ticker_and_name_list:
    challengers.append(item.split()[0])
ticker_dict["challengers"] = challengers

url = 'https://www.digrin.com/stocks/list/6-contenders/'
html = requests.get(url).content
df_list = pd.read_html(html)
df = df_list[-1]
ticker_and_name_list = df["Stock"].to_list()
contenders = []
for item in ticker_and_name_list:
    contenders.append(item.split()[0])
ticker_dict["contenders"] = contenders

url = 'https://www.digrin.com/stocks/list/5-champions/'
html = requests.get(url).content
df_list = pd.read_html(html)
df = df_list[-1]
ticker_and_name_list = df["Stock"].to_list()
champions = []
for item in ticker_and_name_list:
    champions.append(item.split()[0])
ticker_dict["champions"] = champions


import json
with open("tickers_lists.json", 'w') as f:
    json.dump(ticker_dict, f, indent=4)