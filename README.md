# Scope
This project downloads stock data and analyzes it by a set of guidelines  
The data is downloaded from yahoo finance

## How to run?
1. download project from github
2. install requirements file (pip install -f requirements.txt)
3. run main.py. A csv file with data will be generated.

It is recommended to use an IDE (such as pycharm) and a virtual env

# Guildelines
## Our guidelines
1. dividend_yield > TBD
2. payout_ratio < TBD
3. debt_return_time[years] < TBD
4. PE < TBD
5. FWD_PE < TBD
6. credit_rating > TBD

## Dividaat guidelines:
1. dividend_yield > 3%

## Hasolidit guidelines
### numerical:
1. dividend grows from year to year, for at least 5 years (hopefully dividend_annual_growth > 10%)
2. dividend_yield should be greater than snp500 (dividend_yield > 1.58%)
3. payout_ratio < 50%
4. long_term_debt / total_available_capital < 0.5
 
### descriptive:
1. is the bussiness easily explainable

## Resources
1. Hasolidit - how to analyse dividend stocks: https://www.hasolidit.com/%D7%90%D7%99%D7%9A-%D7%9C%D7%A0%D7%AA%D7%97-%D7%9E%D7%A0%D7%99%D7%95%D7%AA-%D7%93%D7%99%D7%91%D7%99%D7%93%D7%A0%D7%93-%D7%9B%D7%9E%D7%95-%D7%9E%D7%9C%D7%9B%D7%94
2. Hasolidit - dividend stocks indexes: https://www.hasolidit.com/%D7%93%D7%99%D7%91%D7%99%D7%93%D7%A0%D7%93-%D7%A7%D7%A8%D7%A0%D7%95%D7%AA-%D7%A1%D7%9C
3. Dividaat - example for a portfolio of dividend stocks: https://dividaat.com/