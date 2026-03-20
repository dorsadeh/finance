import math
import pandas as pd
import numpy as np
import webbrowser
import os
from html import escape


def _calc_score(row):
    """
    Calculate an overall score (0-100) based on weighted metrics.
    Weights reflect the Hasolidit article priorities:
    - Dividend growth (DGR + streak) is the most important signal
    - Payout ratio and debt measure sustainability
    - Yield and valuation round out the picture
    """
    score = 0.0
    total_weight = 0.0

    components = [
        # (column, weight, scoring_func)
        ('dividendYield', 15, lambda v: _linear_score(v, 0.01, 0.06)),
        ('payoutRatio', 15, lambda v: _linear_score(1 - v, 0.3, 1.0)),  # lower is better
        ('DGR_5', 20, lambda v: _linear_score(v, -0.02, 0.15)),
        ('growth_streak', 20, lambda v: _linear_score(v, 0, 25)),
        ('debtReturnTimeByEbitda', 15, lambda v: _linear_score(5 - v, 0, 5)),  # lower is better
        ('forwardPE', 15, lambda v: _linear_score(30 - v, 0, 25)),  # lower is better
    ]

    for col, weight, func in components:
        val = row.get(col)
        if pd.isna(val) or val == 'N/A':
            continue
        try:
            v = float(val)
        except (ValueError, TypeError):
            continue
        total_weight += weight
        score += weight * func(v)

    if total_weight == 0:
        return math.nan
    return round(score / total_weight * 100, 1)


def _linear_score(value, low, high):
    """Map value to 0-1 linearly between low and high, clamped."""
    if high == low:
        return 0.5
    return max(0.0, min(1.0, (value - low) / (high - low)))


# Column definitions: (internal_key, display_name, tooltip, format_func)
COLUMNS = [
    ('shortName', 'Name', 'Company name', 'text'),
    ('score', 'Score', 'Overall quality score (0-100) based on yield, payout, DGR, streak, debt, and valuation', 'score'),
    ('dividendYield', 'Div Yield', 'Annual dividend as % of stock price. Higher = more income per dollar invested', 'pct'),
    ('payoutRatio', 'Payout Ratio', 'Fraction of earnings paid as dividends. Below 50% is strong, above 70% is risky', 'pct'),
    ('trailingPE', 'P/E (TTM)', 'Price / Earnings (trailing 12 months). Lower = cheaper valuation', 'dec1'),
    ('forwardPE', 'Fwd P/E', 'Price / Expected future earnings. Lower = cheaper valuation', 'dec1'),
    ('DGR_3', 'DGR 3Y', 'Dividend Growth Rate over last 3 years (exponential fit)', 'pct'),
    ('DGR_5', 'DGR 5Y', 'Dividend Growth Rate over last 5 years (exponential fit)', 'pct'),
    ('DGR_10', 'DGR 10Y', 'Dividend Growth Rate over last 10 years (exponential fit)', 'pct'),
    ('growth_streak', 'Streak', 'Consecutive years of dividend increases', 'int'),
    ('debtReturnTimeByEbitda', 'Debt/EBITDA', 'Years to repay net debt from EBITDA. Lower = stronger balance sheet', 'dec1'),
    ('debtReturnTimeByIncome', 'Debt/Income', 'Years to repay net debt from net income. Lower = stronger balance sheet', 'dec1'),
    ('growth', 'Price Growth %', 'Total stock price appreciation over the analysis period', 'pct1'),
    ('price_today', 'Price', 'Current stock price', 'usd'),
]


def _fmt(val, fmt_type):
    """Format a value for display."""
    if pd.isna(val) or val == 'N/A':
        return 'N/A'
    try:
        v = float(val)
    except (ValueError, TypeError):
        return escape(str(val))
    if fmt_type == 'pct':
        return f'{v:.2%}'
    if fmt_type == 'pct1':
        return f'{v:.1f}%'
    if fmt_type == 'dec1':
        return f'{v:.1f}'
    if fmt_type == 'int':
        return f'{int(v)}'
    if fmt_type == 'usd':
        return f'${v:.2f}'
    if fmt_type == 'score':
        return f'{v:.0f}'
    return escape(str(val))


def _sort_key(val, fmt_type):
    """Return a numeric sort key for JavaScript data attributes."""
    if pd.isna(val) or val == 'N/A':
        return ''
    try:
        return str(float(val))
    except (ValueError, TypeError):
        return escape(str(val)) if fmt_type == 'text' else ''


def _cell_style(val, col, yield_min, payout_max, debt_max):
    """Return background/text CSS for a cell."""
    if pd.isna(val) or val == 'N/A':
        return 'background-color:#f0f0f0;color:#999'
    try:
        v = float(val)
    except (ValueError, TypeError):
        return ''

    g = 'background-color:#d4edda;color:#155724'
    y = 'background-color:#fff3cd;color:#856404'
    r = 'background-color:#f8d7da;color:#721c24'

    if col == 'score':
        if v >= 70: return g
        if v >= 45: return y
        if v >= 0: return r
        return ''
    if col == 'dividendYield':
        if v >= yield_min * 1.5: return g
        if v >= yield_min: return y
        return r
    if col == 'payoutRatio':
        if v <= payout_max * 0.7: return g
        if v <= payout_max: return y
        return r
    if col in ('debtReturnTimeByEbitda', 'debtReturnTimeByIncome'):
        if v < 0: return g
        if v <= debt_max * 0.6: return g
        if v <= debt_max: return y
        return r
    if col in ('DGR_3', 'DGR_5', 'DGR_10'):
        if v >= 0.10: return g
        if v >= 0.03: return y
        if v < 0: return r
        return ''
    if col == 'growth_streak':
        if v >= 20: return g
        if v >= 10: return y
        if v < 5: return r
        return ''
    if col in ('trailingPE', 'forwardPE'):
        if 0 < v <= 15: return g
        if v <= 25: return y
        if v > 25: return r
    return ''


def _build_html_table(df, yield_min, payout_max, debt_max, table_id):
    """Build a raw HTML table with data-sort attributes and tooltips."""
    available = [(key, name, tip, fmt) for key, name, tip, fmt in COLUMNS if key in df.columns]

    rows_html = []
    for _, row in df.iterrows():
        ticker = escape(str(row.get('Ticker', '')))
        cells = f'<td style="text-align:left;font-weight:bold" data-sort="{ticker}">{ticker}</td>'
        for key, _, _, fmt in available:
            val = row[key]
            style = _cell_style(val, key, yield_min, payout_max, debt_max)
            displayed = _fmt(val, fmt)
            sort_val = _sort_key(val, fmt)
            align = ' text-align:left;' if fmt == 'text' else ''
            cells += f'<td style="{style}{align}" data-sort="{sort_val}">{displayed}</td>'
        rows_html.append(f'<tr>{cells}</tr>')

    # Header
    header_cells = '<th data-col="0" title="Stock ticker symbol">Ticker</th>'
    for i, (key, name, tip, fmt) in enumerate(available, start=1):
        header_cells += f'<th data-col="{i}" title="{escape(tip)}">{escape(name)}</th>'

    return f"""<table id="{table_id}">
<thead><tr>{header_cells}</tr></thead>
<tbody>{''.join(rows_html)}</tbody>
</table>"""


def generate_html_report(raw_csv_path: str, filtered_csv_path: str, settings, output_path: str = "report.html"):
    """
    Generates a styled HTML report from the raw and filtered CSV data.
    Opens the report in the default browser.
    """
    df_raw = pd.read_csv(raw_csv_path)
    df_filtered = pd.read_csv(filtered_csv_path)

    yield_min = settings.dividend_yield_min_val
    payout_max = settings.payout_ratio_max_val
    debt_ebitda_max = settings.debt_return_time_max_val_by_ebitda

    for df in [df_raw, df_filtered]:
        if 'debtReturnTimeByEbitda' not in df.columns:
            df['debtReturnTimeByEbitda'] = (df['totalDebt'] - df['totalCash']) / df['ebitda']
        if 'debtReturnTimeByIncome' not in df.columns:
            df['debtReturnTimeByIncome'] = (df['totalDebt'] - df['totalCash']) / df['netIncomeToCommon']
        df['score'] = df.apply(_calc_score, axis=1)

    # Sort filtered by score descending
    df_filtered = df_filtered.sort_values('score', ascending=False).reset_index(drop=True)
    df_raw = df_raw.sort_values('score', ascending=False).reset_index(drop=True)

    filtered_table = _build_html_table(df_filtered, yield_min, payout_max, debt_ebitda_max, 'tbl-filtered')
    all_table = _build_html_table(df_raw, yield_min, payout_max, debt_ebitda_max, 'tbl-all')

    n_total = len(df_raw)
    n_filtered = len(df_filtered)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Dividend Stock Screener Report</title>
<style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        background: #f5f6fa;
        color: #2c3e50;
        padding: 20px;
    }}
    .header {{
        text-align: center;
        padding: 30px 20px;
        margin-bottom: 24px;
        background: linear-gradient(135deg, #2c3e50, #3498db);
        color: white;
        border-radius: 12px;
    }}
    .header h1 {{ font-size: 28px; margin-bottom: 8px; }}
    .header p {{ font-size: 14px; opacity: 0.85; }}
    .stats {{
        display: flex;
        gap: 16px;
        justify-content: center;
        margin: 20px 0;
        flex-wrap: wrap;
    }}
    .stat-card {{
        background: white;
        border-radius: 10px;
        padding: 16px 24px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        text-align: center;
        min-width: 160px;
    }}
    .stat-card .value {{ font-size: 28px; font-weight: bold; color: #2c3e50; }}
    .stat-card .label {{ font-size: 12px; color: #7f8c8d; margin-top: 4px; }}
    .section {{
        margin: 24px 0;
        background: white;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        overflow: hidden;
    }}
    .section-header {{
        padding: 16px 20px;
        font-size: 18px;
        font-weight: 600;
        border-bottom: 1px solid #e0e0e0;
        cursor: pointer;
        user-select: none;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    .section-header:hover {{ background: #f8f9fa; }}
    .section-header .toggle {{ font-size: 14px; color: #7f8c8d; }}
    .section-body {{
        overflow-x: auto;
        max-height: 70vh;
        overflow-y: auto;
    }}
    .section-body.collapsed {{ display: none; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th {{
        background-color: #2c3e50;
        color: white;
        padding: 8px 12px;
        text-align: center;
        font-size: 13px;
        border-bottom: 2px solid #1a252f;
        position: sticky;
        top: 0;
        z-index: 1;
        cursor: pointer;
        user-select: none;
        white-space: nowrap;
    }}
    th:hover {{ background-color: #3a5068; }}
    th::after {{
        content: '';
        display: inline-block;
        width: 0;
        height: 0;
        margin-left: 6px;
        vertical-align: middle;
    }}
    th.sort-asc::after {{
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-bottom: 5px solid white;
    }}
    th.sort-desc::after {{
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 5px solid white;
    }}
    td {{
        padding: 6px 12px;
        text-align: center;
        font-size: 13px;
        border-bottom: 1px solid #e0e0e0;
    }}
    tr:hover td {{ background-color: #eaf2f8 !important; }}
    th:first-child, td:first-child {{
        text-align: left;
        font-weight: bold;
    }}
    th:nth-child(2), td:nth-child(2) {{
        text-align: left;
    }}
    .legend {{
        display: flex;
        gap: 16px;
        justify-content: center;
        margin: 16px 0;
        flex-wrap: wrap;
        font-size: 13px;
    }}
    .legend-item {{
        display: flex;
        align-items: center;
        gap: 6px;
    }}
    .legend-color {{
        width: 16px;
        height: 16px;
        border-radius: 3px;
        border: 1px solid #ccc;
    }}
    .thresholds {{
        text-align: center;
        font-size: 13px;
        color: #7f8c8d;
        margin: 12px 0;
    }}
    .score-info {{
        text-align: center;
        font-size: 12px;
        color: #95a5a6;
        margin: 4px 0 16px 0;
    }}
</style>
</head>
<body>

<div class="header">
    <h1>Dividend Stock Screener</h1>
    <p>Generated report with color-coded metrics — click any column header to sort</p>
</div>

<div class="stats">
    <div class="stat-card">
        <div class="value">{n_total}</div>
        <div class="label">Total Stocks Analyzed</div>
    </div>
    <div class="stat-card">
        <div class="value">{n_filtered}</div>
        <div class="label">Passed All Filters</div>
    </div>
    <div class="stat-card">
        <div class="value">{n_total - n_filtered}</div>
        <div class="label">Filtered Out</div>
    </div>
</div>

<div class="thresholds">
    Filters: Div Yield &gt; {yield_min:.1%} &nbsp;|&nbsp; Payout Ratio &lt; {payout_max:.0%} &nbsp;|&nbsp; Debt/EBITDA &lt; {debt_ebitda_max:.0f} years
</div>

<div class="legend">
    <div class="legend-item"><div class="legend-color" style="background:#d4edda"></div> Strong</div>
    <div class="legend-item"><div class="legend-color" style="background:#fff3cd"></div> Acceptable</div>
    <div class="legend-item"><div class="legend-color" style="background:#f8d7da"></div> Weak / Failing</div>
    <div class="legend-item"><div class="legend-color" style="background:#f0f0f0"></div> No Data</div>
</div>

<div class="score-info">
    Score weights: DGR 5Y (20%) + Growth Streak (20%) + Div Yield (15%) + Payout Ratio (15%) + Debt/EBITDA (15%) + Fwd P/E (15%)
</div>

<div class="section">
    <div class="section-header" onclick="toggle('filtered')">
        Filtered Results ({n_filtered} stocks)
        <span class="toggle" id="filtered-toggle">collapse</span>
    </div>
    <div class="section-body" id="filtered">
        {filtered_table}
    </div>
</div>

<div class="section">
    <div class="section-header" onclick="toggle('all')">
        All Stocks ({n_total} stocks)
        <span class="toggle" id="all-toggle">expand</span>
    </div>
    <div class="section-body collapsed" id="all">
        {all_table}
    </div>
</div>

<script>
function toggle(id) {{
    var body = document.getElementById(id);
    var txt = document.getElementById(id + '-toggle');
    body.classList.toggle('collapsed');
    txt.textContent = body.classList.contains('collapsed') ? 'expand' : 'collapse';
}}

document.querySelectorAll('th[data-col]').forEach(function(th) {{
    th.addEventListener('click', function() {{
        var table = th.closest('table');
        var colIdx = parseInt(th.getAttribute('data-col'));
        var tbody = table.querySelector('tbody');
        var rows = Array.from(tbody.querySelectorAll('tr'));

        // Determine sort direction
        var asc = !th.classList.contains('sort-asc');
        table.querySelectorAll('th').forEach(function(h) {{
            h.classList.remove('sort-asc', 'sort-desc');
        }});
        th.classList.add(asc ? 'sort-asc' : 'sort-desc');

        rows.sort(function(a, b) {{
            var aVal = a.children[colIdx].getAttribute('data-sort');
            var bVal = b.children[colIdx].getAttribute('data-sort');
            var aNum = parseFloat(aVal);
            var bNum = parseFloat(bVal);

            // Push empty values to the bottom always
            if (aVal === '' && bVal === '') return 0;
            if (aVal === '') return 1;
            if (bVal === '') return -1;

            if (!isNaN(aNum) && !isNaN(bNum)) {{
                return asc ? aNum - bNum : bNum - aNum;
            }}
            return asc ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
        }});

        rows.forEach(function(row) {{ tbody.appendChild(row); }});
    }});
}});
</script>

</body>
</html>"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    abs_path = os.path.abspath(output_path)
    print(f"Report saved to {abs_path}")
    try:
        webbrowser.open('file://' + abs_path)
    except Exception:
        pass
