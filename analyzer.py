import math
import numpy as np
import pandas as pd
import scipy as cp

DAYS_PER_YEAR = 365

class Analyzer():
    #TODO: Doc this class
    def __init__(self, dividends_df: pd.core.series.Series, DGR_years: float) -> None:
        self.dividends_df = dividends_df
        self.DGR_years = DGR_years
        self._dividends_by_year = pd.DataFrame({"Year": [], "Dividends": []})
        self.number_of_events = dividends_df.size
        self.events_t = dividends_df["Date"].values
        t_ns = np.datetime64('today') - self.events_t
        self.t_days = t_ns.astype('timedelta64[D]')
        self.t_years = -self.t_days.astype('float64')/DAYS_PER_YEAR
        self.divs_values = dividends_df["Dividends"].values
        
        
        self._DGR = math.nan
        self._mean_time_between_events = math.nan
        self._growth_streak = math.nan
        self._always_monotonic = False
        self._persistency = []
        self._always_persistent = False
        
        if self.number_of_events > 2:
            self.cal_yearly_dividends()
            self.cal_DGR()
            self.cal_monotonicity()
            self.cal_persistency()
    
    def get_compact_data(self) -> dict:
        return {
            "DGR": self._DGR,
            "mean_time_between_dividends": self._mean_time_between_events,
            "growth_streak": self._growth_streak,
            "always_monotonic": self._always_monotonic,
            "always_persistent": self._always_persistent
        }

    @property
    def DGR(self) -> float:
        return self._DGR
    
    @property
    def mean_time_between_dividends(self) -> float:
        return self._mean_time_between_events
    
    @property
    def growth_streak(self) -> float:
        return self._growth_streak
    
    @property
    def always_monotonic(self) -> bool:
        return self._always_monotonic
    
    @property
    def persistency(self) -> np.ndarray:
        return self._persistency
    
    @property
    def always_persistent(self) -> bool:
        return self._always_persistent

    def cal_yearly_dividends(self):
        years = self.dividends_df["Date"].values.astype("datetime64[Y]").astype(int)+1970
        firt_year = np.min(years)
        last_year = np.datetime64('now').astype("datetime64[Y]").astype(int)+1970
        divs = self.dividends_df["Dividends"].values
        for year in range(firt_year, last_year):
            yearly_div = np.sum(divs[years == year])
            self._dividends_by_year.loc[len(self._dividends_by_year.index)] = [year, yearly_div]    

    def cal_DGR(self):
        """
        This function fits the data from the last number_of_years to an exponential model and calculates dividend growth rate (DGR)
        """
        divs = self._dividends_by_year["Dividends"].values[-self.DGR_years:]
        divs_log = np.log(divs)
        linreg_result = cp.stats.linregress(range(self.DGR_years), divs_log)
        self._DGR = (np.exp(linreg_result.slope)-1)

    def cal_monotonicity(self):
        # checking if dividends are monotonically increasing
        divs_shift = np.roll(self.divs_values, 1)
        divs_shift[0] = divs_shift[1]
        monotonic_test = self.divs_values - divs_shift >=0

        # Calculate growth streak
        drops = np.nonzero(~monotonic_test)[0]
        if drops.size == 0:
            self._growth_streak = self.divs_values.size
        else:
            last_drop = drops[-1]
            self._growth_streak = self.divs_values.size - last_drop

    def cal_persistency(self):
        """
        This function finds where and if the time between two events exceeded twice the **average** of the time between two events, and determine always_persistent value
        """
        t = self.t_days
        t_shift = np.roll(t, 1)
        t_shift[0] = t_shift[1]
        dts = t_shift - t
        dts = dts.astype(float)
        self._mean_time_between_events = np.average(dts[1:])
        self._persistency = dts < self._mean_time_between_events*2
        self._always_persistent = self.persistency.all()