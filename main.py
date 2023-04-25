# %%
import os.path
import yfinance as yf
import pandas as pd
import numpy as np
import scipy as cp

# %%
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
    DIVIDEND_YIELD_MIN_VAL = 0.020
    PAYOUT_RATIO_MAX_VAL = 0.7
    DEBT_RETURN_TIME_MAX_VAL = 5.0

    print("======= all data ======")
    df1 = pd.read_csv(output_file_name)
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

    print("\n======= sort by dividendYield ======")
    df5 = df4.sort_values(by=['dividendYield'], ascending=False)
    df5['isDividendAristocrat'] = df5['Unnamed: 0'].isin(dividend_aristocrats)
    df5['isDefenceCompany'] = df5['Unnamed: 0'].isin(defence_companies_list)
    df5['isInIdoList'] = df5['Unnamed: 0'].isin(ido_list)
    df5['isInDividaatList'] = df5['Unnamed: 0'].isin(dividaat_list)
    print(df5.to_string())

def cal_dev_increament(devs, p):
    # This function calculate the average exponential increments of the devidend
    # and check wheter it is monotonically increasing and if it persistent with maximal time between devidets of 100 days
    #  finding the events during the last p years
    t_abs = devs.index.values
    t_ns = np.datetime64('today')-t_abs
    t_D = t_ns.astype('timedelta64[D]')
    t = -t_D.astype('float64')/365
    last_events = t>-p
    t = t[last_events]
    devs_values = devs.values[last_events]

    # fiting to exponential model
    devs_values_log = np.log(devs_values)
    linreg = cp.stats.linregress(t, devs_values_log)
    yearly_increment = np.exp(linreg.slope)-1

    # checking if devidants are monotonically increasing
    devs_shift = np.roll(devs_values, 1)
    devs_shift[0] = devs_shift[1]
    monotonic_test = devs_values - devs_shift >=0
    is_monotonic = monotonic_test.all()

    # checking if period between devidents exceeded 100 days
    t_D = t*365
    t_D_shift = np.roll(t_D, 1)
    t_D_shift[0] = t_D_shift[1]
    persistant_test = t_D - t_D_shift < 100
    is_persistent= persistant_test.all()

    return yearly_increment, is_monotonic, is_persistent
# %%

dividend_aristocrats = ['DOV','GPC','PG','EMR','MMM','CINF','KO','JNJ','CL','ITW','HRL','SWK','FRT','SYY','GWW','BDX','PPG','TGT','ABBV','ABT','KMB','PEP','NUE','SPGI','ADM','WMT','VFC','ED','LOW','ADP','WBA','PNR','MCD','MDT','SHW','BEN','APD','AMCR','XOM','AFL','CTAS','ATO','MKC','TROW','CAH','CLX','CVX','AOS','ECL','WST','ROP','LIN','CAT','CB','EXPD','BRO','ALB','ESS','O','IBM','NEE','CHD','GD']
ido_list = ['JNJ', 'XOM', 'CVX', 'KO', 'MCD', 'RTX', 'IBM', 'ADP', 'TGT', 'ITW', 'CL', 'APD', 'EMR', 'AFL', 'ED', 'WBA', 'GPC', 'CLX', 'FC', 'PII', 'SON', 'LEG', 'MGEE', 'WLYB', 'UVV', 'TDS', 'ARTNA', 'MMM']
defence_companies_list = ['LMT', 'RTX', 'ESLT', 'BA', 'GD', 'NOC', 'BAESY', 'EADSY', 'THLEF', 'SAIC','HII','LHX','GE','HON','LDOS','HII','TDG','TXT']
dividaat_list = ['ALB','BANF','BEN','CAH','CARR','CB','CBSH','CBU','CHRW','ES','GPC','KTB','LANC','LECO','MO','PB','RBCAA','SCL','SWK','TROW','UGI','UMBF','VFC']
tickers = list( set(dividend_aristocrats).union( set(ido_list), set(dividaat_list), set(defence_companies_list) ) )

# Define a list of the metrics we want to retrieve
metrics = ['dividendYield', 'payoutRatio', 'trailingPE', 'forwardPE', 'enterpriseToEbitda', 'totalDebt',
           'totalCash']

output_file_name = 'ticker_data.csv'
force_update_csv_file = False

if __name__ == '__main__':
    csv_file_exists = os.path.exists(output_file_name)
    if csv_file_exists and not force_update_csv_file:
        print("data exists. not updating file...")
    else:
        print("updating data for all tickers")
        get_data()
    process_data()