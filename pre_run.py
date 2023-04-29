import json
import os
import datetime
from dateutil.relativedelta import relativedelta


default_settings = {
    "included_ticker_lists": ["dividend_aristocrats", "dividaat_list"],
    "start_date": datetime.datetime.strftime(datetime.datetime.now() - relativedelta(years=10), '%Y-%m-%d'),
    "end_date": datetime.datetime.strftime(datetime.date.today(), '%Y-%m-%d')
}
        
class Settings():
    def __init__(self) -> None:
        self.user_file_name = './settings.json'
        self.settings = dict

        self._included_ticker_lists = list
        self._start_date = datetime.date
        self._end_date = datetime.date

        self.load_user_settings()

    @property
    def included_ticker_lists(self) -> list:
        return self._included_ticker_lists
    
    @property
    def start_date(self) -> datetime.date:
        return self._start_date
    
    @property
    def end_date(self) -> datetime.date:
        return self._end_date
        
    def load_user_settings(self):
        # test if settings.json file exist, if not we write it
        if not os.path.isfile(self.user_file_name):
            with open(self.user_file_name, 'w') as user_settings_file:
                json.dump(default_settings, user_settings_file, indent=4)
        
        # loading from file
        with open(self.user_file_name, 'r') as user_settings_file:
            user_settings = json.load(user_settings_file)
        
        # fields validation
        missing_fields = []
        for field in list(default_settings.keys()):
            if field not in list(user_settings.keys()):
                missing_fields.append(field)

            if missing_fields:
                raise RuntimeError('The following fields are absent from the settings.json file, please add them and run the code again: ' + str(missing_fields))
        
        # importing to local variables
        self._included_ticker_lists = user_settings['included_ticker_lists']
        self._start_date = datetime.datetime.strptime(user_settings['start_date'], '%Y-%m-%d').date()
        self._end_date = datetime.datetime.strptime(user_settings['end_date'], '%Y-%m-%d').date()
