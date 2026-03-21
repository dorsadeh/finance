import json
import math
import pandas as pd
import numpy as np
import webbrowser
import os


def generate_html_report(raw_csv_path: str, filtered_csv_path: str, settings, output_path: str = "report.html"):
    """
    Generates an interactive HTML report with client-side filtering and scoring.
    All stock data is embedded as JSON; filtering, scoring, and rendering happen in the browser.
    """
    df_raw = pd.read_csv(raw_csv_path)

    # Compute derived columns
    df_raw['debtReturnTimeByEbitda'] = (df_raw['totalDebt'] - df_raw['totalCash']) / df_raw['ebitda']
    df_raw['debtReturnTimeByIncome'] = (df_raw['totalDebt'] - df_raw['totalCash']) / df_raw['netIncomeToCommon']

    # Convert to JSON-safe records (NaN -> null)
    records = df_raw.to_dict(orient='records')
    for rec in records:
        for k, v in rec.items():
            if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                rec[k] = None

    data_json = json.dumps(records)

    # Default filter/score values from settings
    defaults = {
        'yieldMin': settings.dividend_yield_min_val,
        'yieldMax': settings.dividend_yield_max_val,
        'payoutMax': settings.payout_ratio_max_val,
        'debtEbitdaMax': settings.debt_return_time_max_val_by_ebitda,
        'minStreak': int(settings.years_dividends_growth),
        'wYield': 15,
        'wPayout': 15,
        'wDgr5': 20,
        'wStreak': 20,
        'wDebt': 15,
        'wPe': 15,
    }
    defaults_json = json.dumps(defaults)

    html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Dividend Stock Screener</title>
<style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        background: #f5f6fa;
        color: #2c3e50;
        padding: 20px;
    }
    .header {
        text-align: center;
        padding: 30px 20px;
        margin-bottom: 24px;
        background: linear-gradient(135deg, #2c3e50, #3498db);
        color: white;
        border-radius: 12px;
    }
    .header h1 { font-size: 28px; margin-bottom: 8px; }
    .header p { font-size: 14px; opacity: 0.85; }

    .controls-panel {
        background: white;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 24px;
        overflow: hidden;
    }
    .controls-header {
        padding: 16px 20px;
        font-size: 18px;
        font-weight: 600;
        border-bottom: 1px solid #e0e0e0;
        cursor: pointer;
        user-select: none;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .controls-header:hover { background: #f8f9fa; }
    .controls-header .toggle { font-size: 14px; color: #7f8c8d; }
    .controls-body { padding: 20px; }
    .controls-body.collapsed { display: none; }
    .controls-section { margin-bottom: 20px; }
    .controls-section h3 {
        font-size: 14px;
        color: #7f8c8d;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 12px;
    }
    .controls-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
        gap: 12px;
    }
    .control-item {
        display: flex;
        flex-direction: column;
        gap: 4px;
    }
    .control-item label {
        font-size: 12px;
        color: #555;
        font-weight: 500;
    }
    .control-item .input-row {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .control-item input[type=range] {
        flex: 1;
        accent-color: #3498db;
    }
    .control-item .val {
        font-size: 13px;
        font-weight: 600;
        color: #2c3e50;
        min-width: 45px;
        text-align: right;
    }

    .stats {
        display: flex;
        gap: 16px;
        justify-content: center;
        margin: 20px 0;
        flex-wrap: wrap;
    }
    .stat-card {
        background: white;
        border-radius: 10px;
        padding: 16px 24px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        text-align: center;
        min-width: 160px;
    }
    .stat-card .value { font-size: 28px; font-weight: bold; color: #2c3e50; }
    .stat-card .label { font-size: 12px; color: #7f8c8d; margin-top: 4px; }

    .legend {
        display: flex;
        gap: 16px;
        justify-content: center;
        margin: 16px 0;
        flex-wrap: wrap;
        font-size: 13px;
    }
    .legend-item { display: flex; align-items: center; gap: 6px; }
    .legend-color {
        width: 16px; height: 16px;
        border-radius: 3px; border: 1px solid #ccc;
    }

    .section {
        margin: 24px 0;
        background: white;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        overflow: hidden;
    }
    .section-header {
        padding: 16px 20px;
        font-size: 18px;
        font-weight: 600;
        border-bottom: 1px solid #e0e0e0;
        cursor: pointer;
        user-select: none;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .section-header:hover { background: #f8f9fa; }
    .section-header .toggle { font-size: 14px; color: #7f8c8d; }
    .section-body {
        overflow-x: auto;
        max-height: 70vh;
        overflow-y: auto;
    }
    .section-body.collapsed { display: none; }

    table { width: 100%; border-collapse: collapse; }
    th {
        background-color: #2c3e50;
        color: white;
        padding: 8px 12px;
        text-align: center;
        font-size: 13px;
        border-bottom: 2px solid #1a252f;
        position: sticky;
        top: 0; z-index: 1;
        cursor: pointer;
        user-select: none;
        white-space: nowrap;
    }
    th:hover { background-color: #3a5068; }
    th::after {
        content: '';
        display: inline-block;
        width: 0; height: 0;
        margin-left: 6px;
        vertical-align: middle;
    }
    th.sort-asc::after {
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-bottom: 5px solid white;
    }
    th.sort-desc::after {
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 5px solid white;
    }
    td {
        padding: 6px 12px;
        text-align: center;
        font-size: 13px;
        border-bottom: 1px solid #e0e0e0;
    }
    tr:hover td { background-color: #eaf2f8 !important; }
    th:first-child, td:first-child { text-align: left; font-weight: bold; }
    th:nth-child(2), td:nth-child(2) { text-align: left; }
</style>
</head>
<body>

<div class="header">
    <h1>Dividend Stock Screener</h1>
    <p>Interactive filters and scoring — adjust controls below, table updates live</p>
</div>

<div class="controls-panel">
    <div class="controls-header" onclick="togglePanel('controls-body')">
        Filters & Score Weights
        <span class="toggle" id="controls-body-toggle">collapse</span>
    </div>
    <div class="controls-body" id="controls-body">
        <div class="controls-section">
            <h3>Filters</h3>
            <div class="controls-grid">
                <div class="control-item">
                    <label>Min Dividend Yield</label>
                    <div class="input-row">
                        <input type="range" id="f-yieldMin" min="0" max="10" step="0.5" />
                        <span class="val" id="v-yieldMin"></span>
                    </div>
                </div>
                <div class="control-item">
                    <label>Max Dividend Yield</label>
                    <div class="input-row">
                        <input type="range" id="f-yieldMax" min="3" max="30" step="1" />
                        <span class="val" id="v-yieldMax"></span>
                    </div>
                </div>
                <div class="control-item">
                    <label>Max Payout Ratio</label>
                    <div class="input-row">
                        <input type="range" id="f-payoutMax" min="10" max="100" step="5" />
                        <span class="val" id="v-payoutMax"></span>
                    </div>
                </div>
                <div class="control-item">
                    <label>Max Debt/EBITDA (years)</label>
                    <div class="input-row">
                        <input type="range" id="f-debtEbitdaMax" min="1" max="15" step="0.5" />
                        <span class="val" id="v-debtEbitdaMax"></span>
                    </div>
                </div>
                <div class="control-item">
                    <label>Min Growth Streak (years)</label>
                    <div class="input-row">
                        <input type="range" id="f-minStreak" min="0" max="25" step="1" />
                        <span class="val" id="v-minStreak"></span>
                    </div>
                </div>
            </div>
        </div>
        <div class="controls-section">
            <h3>Score Weights (total shown at right)</h3>
            <div class="controls-grid">
                <div class="control-item">
                    <label>Dividend Yield</label>
                    <div class="input-row">
                        <input type="range" id="w-wYield" min="0" max="50" step="5" />
                        <span class="val" id="v-wYield"></span>
                    </div>
                </div>
                <div class="control-item">
                    <label>Payout Ratio</label>
                    <div class="input-row">
                        <input type="range" id="w-wPayout" min="0" max="50" step="5" />
                        <span class="val" id="v-wPayout"></span>
                    </div>
                </div>
                <div class="control-item">
                    <label>DGR 5Y</label>
                    <div class="input-row">
                        <input type="range" id="w-wDgr5" min="0" max="50" step="5" />
                        <span class="val" id="v-wDgr5"></span>
                    </div>
                </div>
                <div class="control-item">
                    <label>Growth Streak</label>
                    <div class="input-row">
                        <input type="range" id="w-wStreak" min="0" max="50" step="5" />
                        <span class="val" id="v-wStreak"></span>
                    </div>
                </div>
                <div class="control-item">
                    <label>Debt/EBITDA</label>
                    <div class="input-row">
                        <input type="range" id="w-wDebt" min="0" max="50" step="5" />
                        <span class="val" id="v-wDebt"></span>
                    </div>
                </div>
                <div class="control-item">
                    <label>Fwd P/E</label>
                    <div class="input-row">
                        <input type="range" id="w-wPe" min="0" max="50" step="5" />
                        <span class="val" id="v-wPe"></span>
                    </div>
                </div>
                <div class="control-item">
                    <label><strong>Total Weight</strong></label>
                    <div class="input-row">
                        <span class="val" id="v-wTotal" style="font-size:16px;min-width:auto"></span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<div class="stats">
    <div class="stat-card">
        <div class="value" id="stat-total">0</div>
        <div class="label">Total Stocks</div>
    </div>
    <div class="stat-card">
        <div class="value" id="stat-passed">0</div>
        <div class="label">Passed Filters</div>
    </div>
    <div class="stat-card">
        <div class="value" id="stat-filtered">0</div>
        <div class="label">Filtered Out</div>
    </div>
</div>

<div class="legend">
    <div class="legend-item"><div class="legend-color" style="background:#d4edda"></div> Strong</div>
    <div class="legend-item"><div class="legend-color" style="background:#fff3cd"></div> Acceptable</div>
    <div class="legend-item"><div class="legend-color" style="background:#f8d7da"></div> Weak / Failing</div>
    <div class="legend-item"><div class="legend-color" style="background:#f0f0f0"></div> No Data</div>
</div>

<div class="section">
    <div class="section-header" onclick="togglePanel('results-body')">
        <span id="results-title">Filtered Results</span>
        <span class="toggle" id="results-body-toggle">collapse</span>
    </div>
    <div class="section-body" id="results-body">
        <table id="tbl-results">
            <thead><tr id="tbl-header"></tr></thead>
            <tbody id="tbl-body"></tbody>
        </table>
    </div>
</div>

<script>
const ALL_DATA = """ + data_json + """;
const DEFAULTS = """ + defaults_json + """;

const COLS = [
    { key: 'Ticker',               label: 'Ticker',        tip: 'Stock ticker symbol',                                                    fmt: 'text',  align: 'left' },
    { key: 'shortName',            label: 'Name',          tip: 'Company name',                                                           fmt: 'text',  align: 'left' },
    { key: 'score',                label: 'Score',         tip: 'Overall quality score (0-100) computed from the weighted metrics below',  fmt: 'score', align: 'center' },
    { key: 'dividendYield',        label: 'Div Yield',     tip: 'Annual dividend as % of stock price',                                    fmt: 'pct',   align: 'center' },
    { key: 'payoutRatio',          label: 'Payout Ratio',  tip: 'Fraction of earnings paid as dividends',                                 fmt: 'pct',   align: 'center' },
    { key: 'trailingPE',           label: 'P/E (TTM)',     tip: 'Price / Earnings (trailing 12 months)',                                   fmt: 'dec1',  align: 'center' },
    { key: 'forwardPE',            label: 'Fwd P/E',       tip: 'Price / Expected future earnings',                                       fmt: 'dec1',  align: 'center' },
    { key: 'DGR_3',                label: 'DGR 3Y',        tip: 'Dividend Growth Rate over 3 years',                                      fmt: 'pct',   align: 'center' },
    { key: 'DGR_5',                label: 'DGR 5Y',        tip: 'Dividend Growth Rate over 5 years',                                      fmt: 'pct',   align: 'center' },
    { key: 'DGR_10',               label: 'DGR 10Y',       tip: 'Dividend Growth Rate over 10 years',                                     fmt: 'pct',   align: 'center' },
    { key: 'growth_streak',        label: 'Streak',        tip: 'Consecutive years of dividend increases',                                 fmt: 'int',   align: 'center' },
    { key: 'debtReturnTimeByEbitda',label: 'Debt/EBITDA',  tip: 'Years to repay net debt from EBITDA',                                    fmt: 'dec1',  align: 'center' },
    { key: 'debtReturnTimeByIncome',label: 'Debt/Income',  tip: 'Years to repay net debt from net income',                                fmt: 'dec1',  align: 'center' },
    { key: 'growth',               label: 'Price Growth %',tip: 'Total stock price appreciation',                                         fmt: 'pct1',  align: 'center' },
    { key: 'price_today',          label: 'Price',         tip: 'Current stock price',                                                    fmt: 'usd',   align: 'center' },
];

// ---- Formatting ----
function fmtVal(v, fmt) {
    if (v == null || v === 'N/A') return 'N/A';
    if (fmt === 'text') return String(v);
    var n = parseFloat(v);
    if (isNaN(n)) return String(v);
    if (fmt === 'pct') return (n * 100).toFixed(2) + '%';
    if (fmt === 'pct1') return n.toFixed(1) + '%';
    if (fmt === 'dec1') return n.toFixed(1);
    if (fmt === 'int') return Math.round(n).toString();
    if (fmt === 'usd') return '$' + n.toFixed(2);
    if (fmt === 'score') return Math.round(n).toString();
    return String(v);
}

// ---- Color coding ----
function cellStyle(v, key, filters) {
    if (v == null || v === 'N/A') return 'background-color:#f0f0f0;color:#999';
    var n = parseFloat(v);
    if (isNaN(n)) return '';
    var g = 'background-color:#d4edda;color:#155724';
    var y = 'background-color:#fff3cd;color:#856404';
    var r = 'background-color:#f8d7da;color:#721c24';

    if (key === 'score') { return n >= 70 ? g : n >= 45 ? y : r; }
    if (key === 'dividendYield') {
        var ym = filters.yieldMin / 100;
        return n >= ym * 1.5 ? g : n >= ym ? y : r;
    }
    if (key === 'payoutRatio') {
        var pm = filters.payoutMax / 100;
        return n <= pm * 0.7 ? g : n <= pm ? y : r;
    }
    if (key === 'debtReturnTimeByEbitda' || key === 'debtReturnTimeByIncome') {
        if (n < 0) return g;
        return n <= filters.debtEbitdaMax * 0.6 ? g : n <= filters.debtEbitdaMax ? y : r;
    }
    if (key === 'DGR_3' || key === 'DGR_5' || key === 'DGR_10') {
        return n >= 0.10 ? g : n >= 0.03 ? y : n < 0 ? r : '';
    }
    if (key === 'growth_streak') {
        return n >= 20 ? g : n >= 10 ? y : n < 5 ? r : '';
    }
    if (key === 'trailingPE' || key === 'forwardPE') {
        if (n <= 0) return '';
        return n <= 15 ? g : n <= 25 ? y : r;
    }
    return '';
}

// ---- Scoring ----
function linearScore(value, low, high) {
    if (high === low) return 0.5;
    return Math.max(0, Math.min(1, (value - low) / (high - low)));
}

function calcScore(row, weights) {
    var components = [
        { key: 'dividendYield',         w: weights.wYield,   fn: function(v) { return linearScore(v, 0.01, 0.06); } },
        { key: 'payoutRatio',           w: weights.wPayout,  fn: function(v) { return linearScore(1 - v, 0.3, 1.0); } },
        { key: 'DGR_5',                 w: weights.wDgr5,    fn: function(v) { return linearScore(v, -0.02, 0.15); } },
        { key: 'growth_streak',         w: weights.wStreak,  fn: function(v) { return linearScore(v, 0, 25); } },
        { key: 'debtReturnTimeByEbitda', w: weights.wDebt,   fn: function(v) { return linearScore(5 - v, 0, 5); } },
        { key: 'forwardPE',             w: weights.wPe,      fn: function(v) { return linearScore(30 - v, 0, 25); } },
    ];
    var score = 0, totalW = 0;
    for (var i = 0; i < components.length; i++) {
        var c = components[i];
        var val = row[c.key];
        if (val == null || val === 'N/A') continue;
        var n = parseFloat(val);
        if (isNaN(n)) continue;
        totalW += c.w;
        score += c.w * c.fn(n);
    }
    if (totalW === 0) return null;
    return Math.round(score / totalW * 1000) / 10;
}

// ---- Filtering ----
function passesFilters(row, filters) {
    var dy = row.dividendYield;
    if (dy == null) return false;
    if (dy <= filters.yieldMin / 100 || dy >= filters.yieldMax / 100) return false;

    var pr = row.payoutRatio;
    if (pr != null && pr >= filters.payoutMax / 100) return false;

    var de = row.debtReturnTimeByEbitda;
    if (de != null && de >= filters.debtEbitdaMax) return false;

    var gs = row.growth_streak;
    if (gs == null || gs < filters.minStreak) return false;

    return true;
}

// ---- Read controls ----
function readControls() {
    return {
        yieldMin:     parseFloat(document.getElementById('f-yieldMin').value),
        yieldMax:     parseFloat(document.getElementById('f-yieldMax').value),
        payoutMax:    parseFloat(document.getElementById('f-payoutMax').value),
        debtEbitdaMax:parseFloat(document.getElementById('f-debtEbitdaMax').value),
        minStreak:    parseInt(document.getElementById('f-minStreak').value),
        wYield:       parseInt(document.getElementById('w-wYield').value),
        wPayout:      parseInt(document.getElementById('w-wPayout').value),
        wDgr5:        parseInt(document.getElementById('w-wDgr5').value),
        wStreak:      parseInt(document.getElementById('w-wStreak').value),
        wDebt:        parseInt(document.getElementById('w-wDebt').value),
        wPe:          parseInt(document.getElementById('w-wPe').value),
    };
}

function updateDisplayValues(c) {
    document.getElementById('v-yieldMin').textContent = c.yieldMin.toFixed(1) + '%';
    document.getElementById('v-yieldMax').textContent = c.yieldMax + '%';
    document.getElementById('v-payoutMax').textContent = c.payoutMax + '%';
    document.getElementById('v-debtEbitdaMax').textContent = c.debtEbitdaMax.toFixed(1);
    document.getElementById('v-minStreak').textContent = c.minStreak + ' yr';
    document.getElementById('v-wYield').textContent = c.wYield;
    document.getElementById('v-wPayout').textContent = c.wPayout;
    document.getElementById('v-wDgr5').textContent = c.wDgr5;
    document.getElementById('v-wStreak').textContent = c.wStreak;
    document.getElementById('v-wDebt').textContent = c.wDebt;
    document.getElementById('v-wPe').textContent = c.wPe;
    var total = c.wYield + c.wPayout + c.wDgr5 + c.wStreak + c.wDebt + c.wPe;
    document.getElementById('v-wTotal').textContent = total;
    document.getElementById('v-wTotal').style.color = total === 100 ? '#27ae60' : '#e74c3c';
}

// ---- Render table ----
var currentSort = { col: 2, asc: false }; // default: score desc

function renderTable() {
    var c = readControls();
    updateDisplayValues(c);

    var weights = { wYield: c.wYield, wPayout: c.wPayout, wDgr5: c.wDgr5, wStreak: c.wStreak, wDebt: c.wDebt, wPe: c.wPe };
    var filtered = [];
    for (var i = 0; i < ALL_DATA.length; i++) {
        var row = ALL_DATA[i];
        if (!passesFilters(row, c)) continue;
        var copy = Object.assign({}, row);
        copy.score = calcScore(copy, weights);
        filtered.push(copy);
    }

    // Sort
    var sortKey = COLS[currentSort.col].key;
    filtered.sort(function(a, b) {
        var av = a[sortKey], bv = b[sortKey];
        if (av == null && bv == null) return 0;
        if (av == null) return 1;
        if (bv == null) return -1;
        var an = parseFloat(av), bn = parseFloat(bv);
        if (!isNaN(an) && !isNaN(bn)) return currentSort.asc ? an - bn : bn - an;
        return currentSort.asc ? String(av).localeCompare(String(bv)) : String(bv).localeCompare(String(av));
    });

    // Stats
    document.getElementById('stat-total').textContent = ALL_DATA.length;
    document.getElementById('stat-passed').textContent = filtered.length;
    document.getElementById('stat-filtered').textContent = ALL_DATA.length - filtered.length;
    document.getElementById('results-title').textContent = 'Filtered Results (' + filtered.length + ' stocks)';

    // Build rows
    var tbody = document.getElementById('tbl-body');
    var html = '';
    for (var i = 0; i < filtered.length; i++) {
        var row = filtered[i];
        html += '<tr>';
        for (var j = 0; j < COLS.length; j++) {
            var col = COLS[j];
            var val = row[col.key];
            var style = cellStyle(val, col.key, c);
            if (col.align === 'left') style += (style ? ';' : '') + 'text-align:left';
            if (col.key === 'Ticker') style += (style ? ';' : '') + 'font-weight:bold';
            var displayed = fmtVal(val, col.fmt);
            var sortVal = (val == null || val === 'N/A') ? '' : (col.fmt === 'text' ? String(val) : String(parseFloat(val) || ''));
            html += '<td style="' + style + '" data-sort="' + sortVal + '">' + displayed + '</td>';
        }
        html += '</tr>';
    }
    tbody.innerHTML = html;
}

// ---- Build header ----
function buildHeader() {
    var headerRow = document.getElementById('tbl-header');
    for (var i = 0; i < COLS.length; i++) {
        var col = COLS[i];
        var th = document.createElement('th');
        th.textContent = col.label;
        th.setAttribute('title', col.tip);
        th.setAttribute('data-col', i);
        if (i === currentSort.col) th.classList.add(currentSort.asc ? 'sort-asc' : 'sort-desc');
        (function(idx) {
            th.addEventListener('click', function() {
                if (currentSort.col === idx) {
                    currentSort.asc = !currentSort.asc;
                } else {
                    currentSort.col = idx;
                    currentSort.asc = COLS[idx].fmt === 'text';
                }
                // Update header classes
                document.querySelectorAll('#tbl-header th').forEach(function(h) {
                    h.classList.remove('sort-asc', 'sort-desc');
                });
                this.classList.add(currentSort.asc ? 'sort-asc' : 'sort-desc');
                renderTable();
            });
        })(i);
        headerRow.appendChild(th);
    }
}

// ---- Panel toggle ----
function togglePanel(id) {
    var body = document.getElementById(id);
    var txt = document.getElementById(id + '-toggle');
    body.classList.toggle('collapsed');
    txt.textContent = body.classList.contains('collapsed') ? 'expand' : 'collapse';
}

// ---- Init ----
function init() {
    // Set default values on sliders
    document.getElementById('f-yieldMin').value = DEFAULTS.yieldMin * 100;
    document.getElementById('f-yieldMax').value = DEFAULTS.yieldMax * 100;
    document.getElementById('f-payoutMax').value = DEFAULTS.payoutMax * 100;
    document.getElementById('f-debtEbitdaMax').value = DEFAULTS.debtEbitdaMax;
    document.getElementById('f-minStreak').value = DEFAULTS.minStreak;
    document.getElementById('w-wYield').value = DEFAULTS.wYield;
    document.getElementById('w-wPayout').value = DEFAULTS.wPayout;
    document.getElementById('w-wDgr5').value = DEFAULTS.wDgr5;
    document.getElementById('w-wStreak').value = DEFAULTS.wStreak;
    document.getElementById('w-wDebt').value = DEFAULTS.wDebt;
    document.getElementById('w-wPe').value = DEFAULTS.wPe;

    // Attach change listeners
    document.querySelectorAll('.controls-body input[type=range]').forEach(function(input) {
        input.addEventListener('input', renderTable);
    });

    buildHeader();
    renderTable();
}

init();
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
