import math
import numpy as np
import pandas as pd
import scipy as cp

DAYS_PER_YEAR = 365

class Analyzer():
    """
    This class calculates and stores the dividends_by_year DataFram, the DGR for the given number of years (dgr_years)
    """
    def __init__(self, dividends_df: pd.core.series.Series, dgr_years: float) -> None:
        self.dividends_df = dividends_df
        self.dgr_years = dgr_years
        
        self._dividends_by_year = pd.DataFrame({"Year": [], "Dividends": [], "Count": []})
        self._dgr = math.nan
        self._growth_streak = math.nan
        
        if self.dividends_df.size > 2:
            self.cal_yearly_dividends()
            self.cal_dgr()
            self.cal_growth_streak()
    
    def get_compact_data(self) -> dict:
        return {
            "DGR": self._dgr,
            "growth_streak": self._growth_streak,
        }

    @property
    def dividends_by_year(self) -> pd.DataFrame:
        return self._dividends_by_year
    
    @property
    def dgr(self) -> float:
        return self._dgr
    
    @property
    def growth_streak(self) -> float:
        return self._growth_streak
    

    def cal_yearly_dividends(self):
        """
        This function calculated the dividends_by_year DataFrame, which shows how many dividends were given in each year since the company started to share dividends
        """
        years = self.dividends_df["Date"].values.astype("datetime64[Y]").astype(int)+1970
        firt_year = np.min(years)
        last_year = np.datetime64('now').astype("datetime64[Y]").astype(int)+1970
        divs = self.dividends_df["Dividends"].values
        for year in range(firt_year, last_year+1):
            inds = years == year
            yearly_div = np.sum(divs[inds])
            count = inds.sum()
            self._dividends_by_year.loc[len(self._dividends_by_year.index)] = [year, yearly_div, count]    

    def cal_dgr(self):
        """
        This function fits the data from the last number_of_years to an exponential model and calculates dividend growth rate (DGR)
        To avoid negative biases the function discluding the current year
        """
        divs = self._dividends_by_year["Dividends"].values[-self.dgr_years-1:-1]
        divs_log = np.log(divs)
        linreg_result = cp.stats.linregress(range(self.dgr_years), divs_log)
        self._dgr = (np.exp(linreg_result.slope)-1)

    def cal_growth_streak(self):
        """
        This function calculates the growth streak
        """
        divs = self._dividends_by_year["Dividends"].values[:-1]
        divs_shift = np.roll(divs, 1)
        divs_shift[0] = divs_shift[1]
        monotonic_test = divs - divs_shift >0

        # Calculate growth streak
        drops = np.nonzero(~monotonic_test)[0]
        if drops.size == 0:
            self._growth_streak = divs.size
        else:
            last_drop = drops[-1]
            self._growth_streak = divs.size - last_drop