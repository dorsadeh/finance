# %%
import json
import os.path
import sys
import yfinance as yf
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import numpy as np
import scipy as cp
import pre_run

import data_fetcher

# %%
def get_data(metrics: list, tickers: list):
    fetcher = data_fetcher.DataFetcher("downloaded_data")
    fetcher.init_downloads_directory()
    failed_list = []
    cnt = 0
    for ticker in tickers:
        print("downloading ticker " + str(cnt) + "/" + str(len(tickers)))
        cnt += 1
        try:
            fetcher.download_ticker_data(ticker)
        except Exception as e:
            print("Ticker " + ticker + "download failed")
            failed_list.append(ticker)
            continue
    print("failed_list = " + str(failed_list))

    ticker_data = []
    cnt = 1
    for ticker in tickers:
        print("getting data for " + ticker + "  " + str(cnt) + "/" + str(len(tickers)))
        ticker_data.append(fetcher.get_ticker_info(ticker, metrics))
        cnt += 1

    # Convert the list of dictionaries to a Pandas DataFrame
    df = pd.DataFrame(ticker_data, index=tickers)

    # Save the data to a CSV file
    df.to_csv(output_file_name)

def process_data():
    DIVIDEND_YIELD_MIN_VAL = settings.dividend_yield_min_val
    PAYOUT_RATIO_MAX_VAL = settings.payout_ratio_max_val
    DEBT_RETURN_TIME_MAX_VAL_BY_EBITDA = settings.debt_return_time_max_val_by_ebitda
    DEBT_RETURN_TIME_MAX_VAL_BY_INCOME = settings.debt_return_time_max_val_by_income

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
    df4 = df3[(df3['debtReturnTimeByEbitda'] < DEBT_RETURN_TIME_MAX_VAL_BY_EBITDA)  | (df3['debtReturnTimeByEbitda'].isna())]
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
    t_days = t_years*DAYS_PER_YEAR
    t_days_shift = np.roll(t_days, 1)
    t_days_shift[0] = t_days_shift[1]
    persistant_test = t_days - t_days_shift < 100
    is_persistent= persistant_test.all()

    output_dict = {'yearly_increment': yearly_increment,
                   'is_monotonic': is_monotonic,
                   'is_persistent': is_persistent}
    return output_dict


def import_ticker_list() -> list:
    with open("./inputs/tickers.json") as ticker_file:
        tickers_dict = json.load(ticker_file)

    included_ticker_lists = settings.included_ticker_lists
    tickers = []
    for list_name in included_ticker_lists:
        if list_name in included_ticker_lists:
            tickers = tickers +  tickers_dict[list_name]
        else:
            print("Tickers list: " + list_name + ", does not exist in tickers.json")

    return list(set(tickers)) # removes repetitions

# %% run analysis


# Define a list of the metrics we want to retrieve
metrics = ['dividendYield', 'payoutRatio', 'trailingPE', 'forwardPE', 'ebitda', 'totalDebt',
           'totalCash', 'netIncomeToCommon']

output_file_name = 'ticker_data.csv'

if __name__ == '__main__':
    try:
        settings = pre_run.Settings()
    except RuntimeError as e:
        print(e)
        sys.exit()
    tickers = import_ticker_list()
    get_data(metrics, tickers)
    process_data()
# %%
