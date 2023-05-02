import math
import numpy as np
import pandas as pd
import scipy as cp

DAYS_PER_YEAR = 365

class Analyzer():
    """
    This function calculate the average exponential increments of the dividend
    and check wheter it is monotonically increasing and if it persistent with
    maximal time between dividends of 100 days
    """
    def __init__(self, dividends_df: pd.core.series.Series, exp_years: float) -> None:
        self.exp_years = exp_years
        self.number_of_events = dividends_df.size
        self.t_abs = dividends_df["Date"].values
        t_ns = np.datetime64('today') - self.t_abs
        self.t_days = t_ns.astype('timedelta64[D]')
        self.t_years = -self.t_days.astype('float64')/DAYS_PER_YEAR
        self.divs_values = dividends_df["Dividends"].values
        
        self._exp_mean_yearly_growth = math.nan
        self._mean_time_between_events = math.nan
        self._growth_streak = math.nan
        self._always_monotonic = False
        self._persistency = []
        self._always_persistent = False
        
        if self.number_of_events > 2:
            self.exp_growth()
            self.cal_monotonicity()
            self.cal_persistency()
    
    def get_compact_data(self) -> dict:
        return {
            "exp_mean_yearly_growth": self._exp_mean_yearly_growth,
            "mean_time_between_dividends": self._mean_time_between_events,
            "growth_streak": self._growth_streak,
            "always_monotonic": self._always_monotonic,
            "always_persistent": self._always_persistent
        }

    @property
    def exp_mean_yearly_growth(self) -> float:
        return self._exp_mean_yearly_growth
    
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


    def exp_growth(self):
        """
        This function fits the data from the last number_of_years to an exponential model and calculates the exp_mean_yearly_growth
        """
        last_events_indices = self.t_years > -self.exp_years
        t_years_last = self.t_years[last_events_indices]
        divs_values_last = self.divs_values[last_events_indices]
        divs_values_log = np.log(divs_values_last)
        linreg_result = cp.stats.linregress(t_years_last, divs_values_log)
        self._exp_mean_yearly_growth = np.exp(linreg_result.slope)-1

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