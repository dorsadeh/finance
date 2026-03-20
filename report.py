import pandas as pd
import webbrowser
import os

def generate_html_report(raw_csv_path: str, filtered_csv_path: str, settings, output_path: str = "report.html"):
    """
    Generates a styled HTML report from the raw and filtered CSV data.
    Opens the report in the default browser.
    """
    df_raw = pd.read_csv(raw_csv_path, index_col=0)
    df_filtered = pd.read_csv(filtered_csv_path, index_col=0)

    # Thresholds from settings
    yield_min = settings.dividend_yield_min_val
    payout_max = settings.payout_ratio_max_val
    debt_ebitda_max = settings.debt_return_time_max_val_by_ebitda

    # Compute debt return time on raw data too (for the "all" table)
    for df in [df_raw, df_filtered]:
        if 'debtReturnTimeByEbitda' not in df.columns:
            df['debtReturnTimeByEbitda'] = (df['totalDebt'] - df['totalCash']) / df['ebitda']
        if 'debtReturnTimeByIncome' not in df.columns:
            df['debtReturnTimeByIncome'] = (df['totalDebt'] - df['totalCash']) / df['netIncomeToCommon']

    # Columns to display and their friendly names
    display_cols = {
        'dividendYield': 'Div Yield',
        'payoutRatio': 'Payout Ratio',
        'trailingPE': 'P/E (TTM)',
        'forwardPE': 'Fwd P/E',
        'DGR_3': 'DGR 3Y',
        'DGR_5': 'DGR 5Y',
        'DGR_10': 'DGR 10Y',
        'growth_streak': 'Growth Streak',
        'debtReturnTimeByEbitda': 'Debt/EBITDA',
        'debtReturnTimeByIncome': 'Debt/Income',
        'growth': 'Price Growth %',
        'price_today': 'Price',
    }

    def _style_cell(val, col, yield_min, payout_max, debt_max):
        """Return CSS style string for a cell based on its metric and value."""
        if pd.isna(val) or val == 'N/A':
            return 'background-color: #f0f0f0; color: #999'

        try:
            v = float(val)
        except (ValueError, TypeError):
            return ''

        green = 'background-color: #d4edda; color: #155724'
        yellow = 'background-color: #fff3cd; color: #856404'
        red = 'background-color: #f8d7da; color: #721c24'

        if col == 'dividendYield':
            if v >= yield_min * 1.5:
                return green
            elif v >= yield_min:
                return yellow
            else:
                return red

        if col == 'payoutRatio':
            if v <= payout_max * 0.7:
                return green
            elif v <= payout_max:
                return yellow
            else:
                return red

        if col in ('debtReturnTimeByEbitda', 'debtReturnTimeByIncome'):
            if v < 0:
                return green  # negative = net cash position
            elif v <= debt_max * 0.6:
                return green
            elif v <= debt_max:
                return yellow
            else:
                return red

        if col in ('DGR_3', 'DGR_5', 'DGR_10'):
            if v >= 0.10:
                return green
            elif v >= 0.03:
                return yellow
            elif v >= 0:
                return ''
            else:
                return red

        if col == 'growth_streak':
            if v >= 20:
                return green
            elif v >= 10:
                return yellow
            elif v >= 5:
                return ''
            else:
                return red

        if col in ('trailingPE', 'forwardPE'):
            if 0 < v <= 15:
                return green
            elif v <= 25:
                return yellow
            elif v > 25:
                return red

        return ''

    def _build_styled_table(df, yield_min, payout_max, debt_max):
        """Build a styled HTML table from a DataFrame."""
        available = [c for c in display_cols if c in df.columns]
        df_display = df[available].copy()
        df_display = df_display.rename(columns=display_cols)

        # Format percentages
        reverse_map = {v: k for k, v in display_cols.items()}
        fmt_pct = ['dividendYield', 'payoutRatio', 'DGR_3', 'DGR_5', 'DGR_10']

        def apply_styles(styler):
            for friendly_name in styler.columns:
                orig_col = reverse_map.get(friendly_name, friendly_name)
                styler = styler.applymap(
                    lambda val, c=orig_col: _style_cell(val, c, yield_min, payout_max, debt_max),
                    subset=[friendly_name]
                )
            return styler

        def fmt_val(val, col):
            if pd.isna(val) or val == 'N/A':
                return 'N/A'
            try:
                v = float(val)
            except (ValueError, TypeError):
                return str(val)
            if col in fmt_pct:
                return f'{v:.2%}'
            if col in ('growth',):
                return f'{v:.1f}%'
            if col in ('trailingPE', 'forwardPE', 'debtReturnTimeByEbitda', 'debtReturnTimeByIncome'):
                return f'{v:.1f}'
            if col == 'growth_streak':
                return f'{int(v)}'
            if col == 'price_today':
                return f'${v:.2f}'
            return f'{v:.2f}'

        # Format values
        for friendly_name in df_display.columns:
            orig_col = reverse_map.get(friendly_name, friendly_name)
            df_display[friendly_name] = df_display[friendly_name].apply(lambda val, c=orig_col: fmt_val(val, c))

        styler = df_display.style.pipe(apply_styles)
        styler = styler.set_table_styles([
            {'selector': 'th', 'props': [
                ('background-color', '#2c3e50'),
                ('color', 'white'),
                ('padding', '8px 12px'),
                ('text-align', 'center'),
                ('font-size', '13px'),
                ('border-bottom', '2px solid #1a252f'),
                ('position', 'sticky'),
                ('top', '0'),
                ('z-index', '1'),
            ]},
            {'selector': 'td', 'props': [
                ('padding', '6px 12px'),
                ('text-align', 'center'),
                ('font-size', '13px'),
                ('border-bottom', '1px solid #e0e0e0'),
            ]},
            {'selector': 'tr:hover td', 'props': [
                ('background-color', '#eaf2f8 !important'),
            ]},
            {'selector': 'th:first-child, td:first-child', 'props': [
                ('text-align', 'left'),
                ('font-weight', 'bold'),
            ]},
        ])
        return styler.to_html()

    filtered_table = _build_styled_table(df_filtered, yield_min, payout_max, debt_ebitda_max)
    all_table = _build_styled_table(df_raw, yield_min, payout_max, debt_ebitda_max)

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
</style>
</head>
<body>

<div class="header">
    <h1>Dividend Stock Screener</h1>
    <p>Generated report with color-coded metrics</p>
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
    var toggleText = document.getElementById(id + '-toggle');
    body.classList.toggle('collapsed');
    toggleText.textContent = body.classList.contains('collapsed') ? 'expand' : 'collapse';
}}
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
