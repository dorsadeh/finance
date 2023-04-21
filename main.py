import os.path

import yfinance as yf
import pandas as pd

dividend_aristocrats = ['DOV','GPC','PG','EMR','MMM','CINF','KO','JNJ','CL','ITW','HRL','SWK','FRT','SYY','GWW','BDX','PPG','TGT','ABBV','ABT','KMB','PEP','NUE','SPGI','ADM','WMT','VFC','ED','LOW','ADP','WBA','PNR','MCD','MDT','SHW','BEN','APD','AMCR','XOM','AFL','CTAS','ATO','MKC','TROW','CAH','CLX','CVX','AOS','ECL','WST','ROP','LIN','CAT','CB','EXPD','BRO','ALB','ESS','O','IBM','NEE','CHD','GD']
ido_list = ['JNJ', 'XOM', 'CVX', 'KO', 'MCD', 'RTX', 'IBM', 'ADP', 'TGT', 'ITW', 'CL', 'APD', 'EMR', 'AFL', 'ED', 'WBA', 'GPC', 'CLX', 'FC', 'PII', 'SON', 'LEG', 'MGEE', 'WLYB', 'UVV', 'TDS', 'ARTNA', 'MMM']
dividaat_list = ['ALB','BANF','BEN','CAH','CARR','CB','CBSH','CBU','CHRW','ES','GPC','KTB','LANC','LECO','MO','PB','RBCAA','SCL','SWK','TROW','UGI','UMBF','VFC']
defence_companies_list = ['LMT', 'RTX', 'ESLT', 'BA', 'GD', 'NOC', 'BAESY', 'EADSY', 'THLEF', 'SAIC','HII','LHX','GE','HON','LDOS','HII','TDG','TXT']
indexes = ['SCHD', 'VIG', 'VYM', 'VNQ','VNQI','RWO','MORT','REZ']

tickers = list( set(dividend_aristocrats).union( set(ido_list), set(dividaat_list), set(defence_companies_list), set(indexes) ) )
# tickers = ['LMT', 'MMM']

start_date = '2013-04-21'  # 10 years ago
end_date = '2023-04-21'  # today

# Define a list of the metrics we want to retrieve
metrics = ['dividendYield', 'payoutRatio', 'trailingPE', 'forwardPE', 'enterpriseToEbitda', 'totalDebt',
           'totalCash']

output_file_name = 'ticker_data.csv'
force_update_csv_file = False

def get_data():
    # Create an empty list to store the data for each ticker
    ticker_data = []
    cnt = 0
    # Loop through each ticker and retrieve the data for the specified metrics
    for ticker in tickers:
        cnt += 1
        # Download the ticker data using yfinance
        print("downloading ticker data for '" + ticker + "' - " + str(cnt) + "/" + str(len(tickers)))
        ticker_info = yf.Ticker(ticker)

        # Get the historical stock prices for the start and end dates
        stock_data = yf.Ticker(ticker).history(start=start_date, end=end_date)
        # Calculate the stock growth in price
        start_price = stock_data['Close'][0]
        end_price = stock_data['Close'][-1]
        # growth = (end_price - start_price) / start_price * 100
        # print(f"The stock price of {ticker} has grown by {growth:.2f}% over the past 10 years. start_price={start_price:.2f}, end_price={end_price:.2f}")

        # Extract the data for the specified metrics and store it in a dictionary
        data = {}
        for metric in metrics:
            try:
                value = ticker_info.info[metric]
            except:
                value = 'N/A'
            data[metric] = value
        data['price_today'] = end_price
        data['price_10_years_ago'] = start_price
        data['growth'] = (end_price - start_price) / start_price * 100

        # Add the ticker's data to the list of data for all tickers
        ticker_data.append(data)

    # Convert the list of dictionaries to a Pandas DataFrame
    df = pd.DataFrame(ticker_data, index=tickers)

    # Save the data to a CSV file
    df.to_csv(output_file_name)

def process_data():
    DIVIDEND_YIELD_MIN_VAL = 0.020
    PAYOUT_RATIO_MAX_VAL = 0.7
    DEBT_RETURN_TIME_MAX_VAL = 5.0

    print("======= all data ======")
    df0 = pd.read_csv(output_file_name)
    df1 = df0.sort_values(by=['dividendYield'], ascending=False)
    print(df1.to_string())

    print("\n======= filter dividend yield ======")
    df2 = df1[df1['dividendYield'] > DIVIDEND_YIELD_MIN_VAL]
    print(df2.to_string())

    print("\n======= filter payout ratio ======")
    df3 = df2[df2['payoutRatio'] < PAYOUT_RATIO_MAX_VAL]
    print(df3.to_string())

    print("\n======= filter debt return time ======")
    df3['debtReturnTime'] = df3['totalDebt'] / df3['totalCash']
    df4 = df3[df3['debtReturnTime'] < DEBT_RETURN_TIME_MAX_VAL]
    print(df4.to_string())

    print("\n======= add lists presense ======")
    df4['isDividendAristocrat'] = df4['Unnamed: 0'].isin(dividend_aristocrats)
    df4['isDefenceCompany'] = df4['Unnamed: 0'].isin(defence_companies_list)
    df4['isInIdoList'] = df4['Unnamed: 0'].isin(ido_list)
    df4['isInDividaatList'] = df4['Unnamed: 0'].isin(dividaat_list)
    print(df4.to_string())

if __name__ == '__main__':
    csv_file_exists = os.path.exists(output_file_name)
    if csv_file_exists and not force_update_csv_file:
        print("data exists. not updating file...")
    else:
        print("updating data for all tickers")
        get_data()
    process_data()
