# %%
import json
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
        # with open("data.json", 'w', encoding='utf-8') as f:
        #     json.dump(ticker_info.info, f, ensure_ascii=False, indent=2)

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
    DEBT_RETURN_TIME_MAX_VAL_BY_EBITDA = 5.0
    DEBT_RETURN_TIME_MAX_VAL_BY_INCOME = 5.0

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
    df3['debtReturnTimeByEbitda'] = (df3['totalDebt'] - df3['totalCash']) / df3['ebitda']
    df3['debtReturnTimeByIncome'] = (df3['totalDebt'] - df3['totalCash']) / df3['netIncomeToCommon']
     # TODO: handle N/A case
    df4 = df3[df3['debtReturnTime'] < DEBT_RETURN_TIME_MAX_VAL_BY_EBITDA]
    print(df4.to_string())

    print("\n======= add lists presense ======")
    df4['isDividendAristocrat'] = df4['Unnamed: 0'].isin(dividend_aristocrats)
    df4['isDefenceCompany'] = df4['Unnamed: 0'].isin(defence_companies_list)
    df4['isInIdoList'] = df4['Unnamed: 0'].isin(ido_list)
    df4['isInDividaatList'] = df4['Unnamed: 0'].isin(dividaat_list)
    print(df4.to_string())
    df4.to_csv("filtered_data.csv")

def cal_dividend_increament(div_obj: pd.core.series.Series, number_of_years: int)-> dict:
    """
    This function calculate the average exponential increments of the dividend
    and check wheter it is monotonically increasing and if it persistent with
    maximal time between dividends of 100 days
    """
    # finding the events during the last p years
    DAYS_PER_YEAR = 365
    t_abs_all = div_obj.index.values
    t_ns_all = np.datetime64('today')-t_abs_all
    t_days_all = t_ns_all.astype('timedelta64[D]')
    t_years = -t_days_all.astype('float64')/DAYS_PER_YEAR
    last_events_indices = t_years>-number_of_years
    t_years = t_years[last_events_indices]
    divs_values = div_obj.values[last_events_indices]

    # fiting to exponential model
    divs_values_log = np.log(divs_values)
    linreg_result = cp.stats.linregress(t_years, divs_values_log)
    yearly_increment = np.exp(linreg_result.slope)-1

    # checking if dividends are monotonically increasing
    divs_shift = np.roll(divs_values, 1)
    divs_shift[0] = divs_shift[1]
    monotonic_test = divs_values - divs_shift >=0
    is_monotonic = monotonic_test.all()

    # checking if period between dividends exceeded 100 days
    t_days = t_years*365
    t_days_shift = np.roll(t_days, 1)
    t_days_shift[0] = t_days_shift[1]
    persistant_test = t_days - t_days_shift < 100
    is_persistent= persistant_test.all()

    output_dict = {'yearly_increment': yearly_increment,
                   'is_monotonic': is_monotonic,
                   'is_persistent': is_persistent}
    return output_dict
# %% import tickers
with open("./inputs/tickers.json") as ticker_file:
    tickers_dict = json.load(ticker_file)

lists_to_include = ["dividend_aristocrats", "dividaat_list"]
tickers = []
for list_name in lists_to_include:
    if list_name in lists_to_include:
        tickers = tickers +  tickers_dict[list_name]
    else:
        print("Tickers list: " + list_name + ", does not exist in tickers.json")

tickers = list(set(tickers)) # remove repetitions

# %% run analysis

start_date = '2013-04-21'  # 10 years ago
end_date = '2023-04-21'  # today

# Define a list of the metrics we want to retrieve
metrics = ['dividendYield', 'payoutRatio', 'trailingPE', 'forwardPE', 'ebitda', 'totalDebt',
           'totalCash', 'netIncomeToCommon']

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