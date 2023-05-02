import math
import numpy as np
import pandas as pd
import scipy as cp

DAYS_PER_YEAR = 365

class analyzer():
    """
    This function calculate the average exponential increments of the dividend
    and check wheter it is monotonically increasing and if it persistent with
    maximal time between dividends of 100 days
    """
    def __init__(self, dividends_df: pd.core.series.Series, number_of_years: int) -> None:
        self.number_of_events = dividends_df.size
        self.t_abs_all = dividends_df["Date"].values
        t_ns_all = np.datetime64('today') - self.t_abs_all
        self.t_days_all = t_ns_all.astype('timedelta64[D]')
        self.t_years_all = -t_days_all.astype('float64')/DAYS_PER_YEAR
        self.divs_values = dividends_df["Dividends"].values
        
        self._exp_mean_yearly_growth = math.nan
        self._mean_time_between_dividends = math.nan
        self._growth_streak = math.nan
        self._always_monotonic = False
        self._persistency = []
        self._always_persistent = False
        
        if self.number_of_events > 2:
            self.exp_growth()
            self.cal_monotonicity()
            self.cal_persistency()

    @property
    def exp_mean_yearly_growth(self) -> float:
        return self._exp_mean_yearly_growth
    
    @property
    def mean_time_between_dividends(self) -> float:
        return self._mean_time_between_dividends
    
    @property
    def exp_mean_yearly_growth(self) -> float:
        return self._exp_mean_yearly_growth
    
    @property
    def exp_mean_yearly_growth(self) -> float:
        return self._exp_mean_yearly_growth
    
    @property
    def exp_mean_yearly_growth(self) -> float:
        return self._exp_mean_yearly_growth
    
    @property
    def exp_mean_yearly_growth(self) -> float:
        return self._exp_mean_yearly_growth


    def exp_growth(self):
        """
        This function fits the data from the last number_of_years to an exponential model and calculates the exp_mean_yearly_growth
        """
        last_events_indices = t_years_all>-number_of_years
        t_years_last = self.t_years_all[last_events_indices]
        divs_values_last = self.divs_values[last_events_indices]
        divs_values_log = np.log(divs_values_last)
        linreg_result = cp.stats.linregress(t_years_last, divs_values_log)
        self._exp_mean_yearly_growth = np.exp(linreg_result.slope)-1

    def cal_monotonicity(self):
        linreg_result = cp.stats.linregress(t_years_last, divs_values_log)
        exp_mean_yearly_growth = np.exp(linreg_result.slope)-1
        # checking if dividends are monotonically increasing
        divs_shift = np.roll(divs_values_last, 1)
        divs_shift[0] = divs_shift[1]
        monotonic_test = divs_values_last - divs_shift >=0

        # Calculate growth streak
        drops = np.nonzero(~monotonic_test)[0]
        if drops.size == 0:
            self.growth_streak = divs_values.size
        else:
            last_drop = drops[-1]
            self.growth_streak = divs_values.size - last_drop

    def cal_persistency(self):
        # finding where and if the time between two events exceeded twice the **average** of the time between two events
        t = self.t_days_all
        t_shift = np.roll(t, 1)
        t_shift[0] = t_shift[1]
        dts = t - t_shift
        self._mean_time_between_dividends = np.average(dts[1:])
        self.persistency = dts < self._mean_time_between_dividends*2
        self.always_persistent = self.persistency.all()