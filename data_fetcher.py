import os
import shutil
import json
import yfinance as yf
from datetime import datetime

class DataFetcher:
    """
    This module downloads data from yahoo finance and saves it locally in a downloads directory
    """
    def __init__(self, directory_path: str, import_start_date: datetime=datetime(2008,1,1)) -> None:
        self.module_version = 1
        self.directory_path = directory_path
        self.start_date = import_start_date
        
    def init_downloads_directory(self, clear_contents: bool=False) -> None:
        """
        checks if a downloads directory exists, and if not, creates it
        if clear flag is set to true, directory is cleared
        """
        # if not os.path.exists(self.directory_path):
        #     os.makedirs(self.directory_path)
        #     print("Directory created:", self.directory_path)
        # else:
        #     print("Directory already exists:", self.directory_path)

        if os.path.exists(self.directory_path):
            if clear_contents:
                shutil.rmtree(self.directory_path)
                print(f"The contents of the directory '{self.directory_path}' have been deleted.")
            else:
                print(f"The directory '{self.directory_path}' already exists.")
        else:
            os.makedirs(self.directory_path)
            print(f"The directory '{self.directory_path}' has been created.")
    
   
    def download_ticker_data(self, ticker:str):
        """
        for each ticker - checks if data is already available for a ticker, and if not downloads
        1. a separate directory is created
        2. the following data is saved: info, dividends price history, stock history
        """
        dir_path = os.path.join(self.directory_path, ticker)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print("Directory created:", dir_path)
        else:
            print("Data exists for ", ticker)
            return

        print("Downloading data for " + dir_path + "...")
        ticker_info = yf.Ticker(ticker)

        # save info json
        info_json_path = os.path.join(dir_path, "info.json")
        with open(info_json_path, 'w') as f:
            json.dump(ticker_info.info, f, indent=4)
        
        # save dividends series
        dividends = ticker_info.dividends
        dividends.to_csv(os.path.join(dir_path, "dividends.csv"))

        # save history series
        history = ticker_info.history(start=self.start_date, end=datetime.now())
        history.to_csv(os.path.join(dir_path, "history.csv"))
