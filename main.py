import os.path

import yfinance as yf
import pandas as pd

# tickers = ['JNJ', 'XOM', 'CVX', 'KO']
tickers = ['JNJ', 'XOM', 'CVX', 'KO', 'MCD', 'RTX', 'IBM', 'ADP', 'TGT', 'ITW', 'CL', 'APD', 'EMR', 'AFL', 'ED', 'WBA', 'GPC', 'CLX', 'FC', 'PII', 'SON', 'LEG', 'MGEE', 'WLYB', 'UVV', 'TDS', 'ARTNA', 'MMM']

# Define a list of the metrics we want to retrieve
metrics = ['dividendYield', 'payoutRatio', 'trailingPE', 'forwardPE', 'enterpriseToEbitda', 'totalDebt',
           'totalCash']

output_file_name = 'ticker_data.csv'
force_update_csv_file = False

def get_data():
    # Create an empty list to store the data for each ticker
    ticker_data = []

    # Loop through each ticker and retrieve the data for the specified metrics
    for ticker in tickers:
        # Download the ticker data using yfinance
        print("===========" + ticker + "===========")
        print("downloading data...")
        ticker_info = yf.Ticker(ticker)

        print("processing data...")
        # Extract the data for the specified metrics and store it in a dictionary
        data = {}
        for metric in metrics:
            try:
                value = ticker_info.info[metric]
            except:
                value = 'N/A'
            data[metric] = value

        # Add the ticker's data to the list of data for all tickers
        ticker_data.append(data)

    # Convert the list of dictionaries to a Pandas DataFrame
    df = pd.DataFrame(ticker_data, index=tickers)

    # Save the data to a CSV file
    df.to_csv(output_file_name)

def process_data():
    DIVIDEND_YIELD_MIN_VAL = 0.025
    PAYOUT_RATIO_MAX_VAL = 0.7

    print("======= all data ======")
    df1 = pd.read_csv(output_file_name)
    print(df1.to_string())

    print("\n======= filter dividend yield ======")
    df2 = df1[df1['dividendYield'] > DIVIDEND_YIELD_MIN_VAL]
    print(df2.to_string())

    print("\n======= filter payout ratio ======")
    df3 = df2[df2['payoutRatio'] < PAYOUT_RATIO_MAX_VAL]
    print(df3.to_string())


if __name__ == '__main__':
    csv_file_exists = os.path.exists(output_file_name)
    if csv_file_exists and not force_update_csv_file:
        print("data exists. not updating file...")
    else:
        print("updating data for all tickers")
        get_data()
    process_data()