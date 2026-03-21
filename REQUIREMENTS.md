# Dividend Stock Screener — Requirements

## Source
Based on [Hasolidit — How to Analyze Dividend Stocks Like a Queen](https://www.hasolidit.com/%d7%90%d7%99%d7%9a-%d7%9c%d7%a0%d7%aa%d7%97-%d7%9e%d7%a0%d7%99%d7%95%d7%aa-%d7%93%d7%99%d7%91%d7%99%d7%93%d7%a0%d7%93-%d7%9b%d7%9e%d7%95-%d7%9e%d7%9c%d7%9b%d7%94), plus additional analysis metrics.

---

## Step 1: Dividend History & Growth
- [x] Company must pay a dividend
- [x] Dividend Growth Rate (DGR) over 3, 5, 10, 20, max years (exponential fit)
- [x] Growth streak (consecutive years of dividend increases)
- [x] Filter: minimum growth streak (default 5 years, configurable)
- [x] Filter: dividend yield > configurable minimum (default 2%)
- [x] Filter: dividend yield < configurable maximum (default 10%)
- [ ] Compare dividend yield to S&P 500 average yield (flag stocks below it)

## Step 2: Business Comprehensibility (Qualitative)
- [ ] Display company sector/industry from yfinance
- [ ] Display company description (longBusinessSummary)
- [ ] Manual notes/flag field (optional enrichment)

## Step 3: Payout Ratio
- [x] EPS-based payout ratio from yfinance
- [x] Filter: payout ratio < configurable max (default 70%)
- [ ] FCF-based payout ratio (freeCashflow / netIncome or dividends / FCF)
- [ ] Flag REITs and sectors where higher payout is normal

## Step 4: Financial Strength
- [x] Debt return time by EBITDA (totalDebt - totalCash) / EBITDA
- [x] Debt return time by income (totalDebt - totalCash) / netIncome
- [x] Filter: debt/EBITDA < configurable max (default 5 years)
- [ ] Debt-to-Equity ratio (debtToEquity from yfinance, prefer < 0.5)
- [ ] Current Ratio (currentRatio from yfinance, must be > 1.0)
- [ ] Interest Coverage Ratio (EBIT / interestExpense, higher = better)
- [ ] Credit Rating (not available from yfinance — external data needed)
- [ ] Trend: is debt declining over time?

## Step 5: Competitive Moat
### Quantitative (Margins)
- [ ] Gross Margin > 40% (grossMargins from yfinance)
- [ ] Operating Margin > 25% (operatingMargins from yfinance)
- [ ] Net Profit Margin > 20% (profitMargins from yfinance)
- [ ] Free Cash Flow Margin > 15% (freeCashflow / totalRevenue)
- [ ] Margin stability over time

### Qualitative
- [ ] Morningstar moat rating (optional CSV/JSON import — Phase 3)
- [ ] Moat source identification (intangible assets, switching costs, barriers)

## Step 6: Growth
- [ ] Revenue growth over 3, 5, 10 years (prefer >= 7%)
- [ ] EPS growth trend over 10 years
- [ ] FCF growth trend over 10 years
- [ ] Flag: large gap between EPS and FCF (low-quality earnings warning)

## Step 7: Efficiency / Returns on Capital
- [ ] ROA — Return on Assets (returnOnAssets from yfinance)
- [ ] ROE — Return on Equity (returnOnEquity from yfinance, target ~15%+)
- [ ] ROIC — Return on Invested Capital (calculated: netIncome / (equity + debt))
- [ ] Stability of returns over time

## Step 8: Management Alignment (Qualitative)
- [ ] Insider ownership percentage (from yfinance insiderHoldings)
- [ ] Insider buying activity (positive signal)
- [ ] Flag family-controlled companies

## Step 9: Share Count Trend
- [ ] sharesOutstanding trend over time (declining = buybacks = positive)
- [ ] Display current shares outstanding

## Step 10: Valuation
- [x] Trailing P/E (trailingPE)
- [x] Forward P/E (forwardPE)
- [ ] Blended P/E (average of trailing and forward)
- [ ] Current dividend yield vs historical average yield (buy when above avg)
- [ ] Current P/E vs historical average P/E (buy when below avg)
- [ ] PEG ratio

---

## Additional Analysis Metrics (beyond article)

### Returns & Benchmarking
- [ ] Total return per stock (price appreciation + reinvested dividends)
- [ ] SPY total return as benchmark (same period)
- [ ] Excess return vs SPY
- [ ] Annualized return

### Risk Metrics
- [ ] Volatility (annualized standard deviation of returns)
- [ ] Sharpe Ratio ((return - risk_free_rate) / volatility)
- [ ] Beta (from yfinance or calculated vs SPY)
- [ ] Max drawdown

### Market Cap
- [ ] Display market cap (marketCap from yfinance)
- [ ] Classify: Large Cap (>$10B), Mid Cap ($2-10B), Small Cap (<$2B)
- [ ] Useful for: liquidity assessment, risk profiling, diversification

---

## Scoring System
- [x] Overall score (0-100) with configurable weights
- [x] Interactive weight adjustment in HTML report
- [ ] Expand scoring to include new metrics as they are implemented

## Report / UI
- [x] HTML report with color-coded metrics
- [x] Interactive filters (client-side)
- [x] Interactive score weights (client-side)
- [x] Column sorting
- [x] Tooltips on all columns
- [ ] Export filtered results from HTML (download CSV button)
- [ ] Charts: dividend growth over time per stock
- [ ] Charts: yield vs growth scatter plot

## Data Pipeline
- [x] yfinance data download and local caching
- [x] Cache validation (detect delisted/garbage data)
- [x] Download retries with backoff
- [x] Delisted tickers tracked in no_data list
- [ ] Cache expiry (re-download data older than N days)
- [ ] Progress bar during download
