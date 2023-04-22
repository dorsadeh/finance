# Scope
This project downloads stock data and analyzes it by a set of guidelines  
The data is downloaded from yahoo finance

## How to run?
1. download project from github
2. install requirements file (pip install -r requirements.txt)
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
1. [Hasolidit - how to analyse dividend stocks like a queen](https://www.hasolidit.com/%d7%90%d7%99%d7%9a-%d7%9c%d7%a0%d7%aa%d7%97-%d7%9e%d7%a0%d7%99%d7%95%d7%aa-%d7%93%d7%99%d7%91%d7%99%d7%93%d7%a0%d7%93-%d7%9b%d7%9e%d7%95-%d7%9e%d7%9c%d7%9b%d7%94)
2. [Hasolidit - dividend stocks indexes](https://www.hasolidit.com/%D7%93%D7%99%D7%91%D7%99%D7%93%D7%A0%D7%93-%D7%A7%D7%A8%D7%A0%D7%95%D7%AA-%D7%A1%D7%9C)
3. [Dividaat - example for a portfolio of dividend stocks](https://dividaat.com)