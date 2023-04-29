# https://finviz.com/screener.ashx?v=111&f=fa_div_o2&ft=4]

import pandas as pd
import requests
import json

ticker_dict = {}
output_file_name = "tickers_lists.json"
source = ["wikipedia", "digrin"]

def get_tickers_list(url:str, source: str) -> dict:
    """
    downloads data from the url and extracts a list of tickers to a list
    """
    # Download the list of S&P 500 companies from Wikipedia
    print("getting data from " + url)
    html = requests.get(url).content
    df_list = pd.read_html(html)
    df = df_list[-1]
    if source == "wikipedia":
        return df["Ticker symbol"].to_list()
    elif source == "digrin":
        ticker_list = []
        for item in df["Stock"].to_list():
            ticker_list.append(item.split()[0])
        return ticker_list
    else:
        print("unspecified source!!!")
        return {}
    

ticker_dict["dividend_aristocrats"] = get_tickers_list('https://en.wikipedia.org/wiki/S%26P_500_Dividend_Aristocrats', "wikipedia")
ticker_dict["challengers"] = get_tickers_list('https://www.digrin.com/stocks/list/7-challengers/', "digrin")
ticker_dict["contenders"] = get_tickers_list('https://www.digrin.com/stocks/list/6-contenders/', "digrin")
ticker_dict["champions"] = get_tickers_list('https://www.digrin.com/stocks/list/5-champions/', "digrin")

print("==================================================")
for item in ticker_dict:
    print(item + " list has " + str(len(ticker_dict[item])) + " tickers")

print("saving data to " + output_file_name)
with open(output_file_name, 'w') as f:
    json.dump(ticker_dict, f, indent=4)