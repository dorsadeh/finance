

# 1-dividends
- does the company give dividends
    look at **"dividendYield"**
    snp500 dividendYield=1.66%

- does the company increment dividend from year to year
    look at the **dividends.csv** report and check that dividend is incremented constantly

# 2-is the bussiness easy to explain
- for the user to define

# 3-payout ratiio
- what part of the company earnings is payed as dividends
    as this ratio is lower it means the dividend is safer
    payoutRatio < 50% is good
    in json file:    "payoutRatio"

# 4-financial strength

## Debt to Equity Ratio
- debtToEquity ratio = (total debt) / (total equity)
    a ratio which is smaller than 100% means that the company funds itself by its own equity
    a ratio which is smaller than 50% can mean that the company has a compatetive advantage
in json file: "debtToEquity"


## long term debt per capital
- long term debt per capital = (long term debt) / (total availale capital)
    this gives an understanding what is the part of the debt from all of the company's funding
in json file:    TBD

## interest coverage
- is the earnings enough to cover expances
    interest coverage = 3 means that the company can cover 3 time its expances with its earnings
in json file:    TBD

## currentRatio
currentRatio = assets / debt
currentRatio > 1 is ok. that means the company has enough assets to cover all her debt
in json file:    "currentRatio"



