import os
import shutil
import json
import pandas as pd
import yfinance as yf
from datetime import datetime
import definitions

defs = definitions.Definitions()
class DataFetcher:
    """
    This module downloads data from yahoo finance and saves it locally in a downloads directory
    """
    def __init__(self, downloaded_data_dir_path: str, import_start_date: datetime=datetime(2008,1,1)) -> None:
        __version__ = "0.1.0"
        self.downloaded_data_dir_path = downloaded_data_dir_path
        self.start_date = import_start_date
        
    def init_downloads_directory(self, clear_contents: bool=False) -> None:
        """
        checks if a downloads directory exists, and if not, creates it
        if clear flag is set to true, directory is cleared
        """
        if os.path.exists(self.downloaded_data_dir_path):
            if clear_contents:
                shutil.rmtree(self.downloaded_data_dir_path)
                print(f"The contents of the directory '{self.downloaded_data_dir_path}' have been deleted.")
            else:
                print(f"The directory '{self.downloaded_data_dir_path}' already exists.")
        else:
            os.makedirs(self.downloaded_data_dir_path)
            print(f"The directory '{self.downloaded_data_dir_path}' has been created.")
    
    def __get_paths(self, ticker:str) -> dict:
        dir_path = os.path.join(self.downloaded_data_dir_path, ticker)
        info_json_path = os.path.join(dir_path, "info.json") 
        dividends_path = os.path.join(dir_path, "dividends.csv")
        stock_history_path = os.path.join(dir_path, "history.csv")
        return {
            "dir_path" : dir_path,
            "info_json_path" : info_json_path,
            "dividends_path" : dividends_path,
            "stock_history_path" : stock_history_path
        }
   
    def download_ticker_data(self, ticker:str):
        """
        for each ticker - checks if data is already available for a ticker, and if not downloads
        1. a separate directory is created
        2. the following data is saved: info, dividends price history, stock history
        """
        paths = self.__get_paths(ticker)
        dir_path = paths["dir_path"]
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print("Directory created:", dir_path)
        else:
            print("Data exists for ", ticker)
            return

        print("Downloading data for " + dir_path + "...")
        try:
            ticker_info = yf.Ticker(ticker)

            # save info json
            with open(paths["info_json_path"], 'w') as f:
                json.dump(ticker_info.info, f, indent=4)

            # save dividends series
            dividends = ticker_info.dividends
            dividends.to_csv(paths["dividends_path"], date_format=defs.date_format)

            # save history series
            history = ticker_info.history(start=self.start_date, end=datetime.now())
            history.to_csv(paths["stock_history_path"])
        except Exception:
            # Remove the directory so the ticker can be retried on next run
            shutil.rmtree(dir_path, ignore_errors=True)
            raise

    
    def get_ticker_info(self, ticker:str, metrics: list) -> dict:
        """
        returns a dictionary of:
        1. all metrics specified in the metrics param
        2. stock price at begining, end and growth
        3. TODO: add dividend consistency info
        """
        dir_path = os.path.join(self.downloaded_data_dir_path, ticker)
        if not os.path.exists(dir_path):
            return {}
       
        paths = self.__get_paths(ticker)
        with open(paths["info_json_path"], "r") as f:
            ticker_info_dict = json.load(f)
        data = {}
        for metric in metrics:
            try:
                value = ticker_info_dict[metric]
            except KeyError:
                value = 'N/A'
            # yfinance >= 1.0 returns dividendYield as percentage (e.g. 2.73 instead of 0.0273)
            if metric == 'dividendYield' and isinstance(value, (int, float)) and value > 1:
                value = value / 100.0
            data[metric] = value

        df = pd.read_csv(paths["stock_history_path"])
        if df.empty or 'Close' not in df.columns:
            data['price_today'] = 'N/A'
            data['price_at_start'] = 'N/A'
            data['growth'] = 'N/A'
        else:
            start_price = df['Close'].iloc[0]
            end_price = df['Close'].iloc[-1]
            data['price_today'] = end_price
            data['price_at_start'] = start_price
            data['growth'] = (end_price - start_price) / start_price * 100
        return data
    
    def get_ticker_dividends_history(self, ticker:str) -> pd.DataFrame:
        dir_path = os.path.join(self.downloaded_data_dir_path, ticker)
        if not os.path.exists(dir_path):
            return pd.DataFrame({"Date": [], "Dividends": []})

        paths = self.__get_paths(ticker)
        data = pd.read_csv(paths["dividends_path"])
        if 'Date' not in data.columns or data.empty:
            return pd.DataFrame({"Date": [], "Dividends": []})
        data['Date'] = pd.to_datetime(data['Date'], utc=True)
        return data