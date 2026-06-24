"""
Build: Arrears & Default Monitoring Dashboard  ->  arrears_default_dashboard.html
Authentic Tableau-style theme (light canvas, worksheet tiles, Tableau 10 palette).
"""
import json, csv, os
from collections import defaultdict

BASE         = os.path.dirname(os.path.abspath(__file__))
DATA_DIR     = os.path.join(BASE, "data")
LOANS_FILE   = os.path.join(DATA_DIR, "loans.csv")
ARREARS_FILE = os.path.join(DATA_DIR, "arrears_monthly.csv")
CLAIMS_FILE  = os.path.join(DATA_DIR, "claims.csv")
OUT          = os.path.join(BASE, "arrears_default_dashboard.html")

# == Load data =================================================================
loans = []
with open(LOANS_FILE, encoding='utf-8') as f:
    for r in csv.DictReader(f):
        loans.append({
            'loan_id':      r['loan_id'],
            'state':        r['state'],
            'lvr_band':     r['lvr_band'],
            'borrower_type':r['borrower_type'],
            'property_type':r['property_type'],
            'employment':   r['employment_type'],
            'status':       r['loan_status'],
            'loan_amt':     float(r['loan_amount']),
            'premium':      float(r['premium_amount']),
        })

arrears = []
with open(ARREARS_FILE, encoding='utf-8') as f:
    for r in csv.DictReader(f):
        arrears.append({
            'date':         r['snapshot_date'],
            'month':        r['snapshot_month'],
            'loan_id':      r['loan_id'],
            'state':        r['state'],
            'lvr_band':     r['lvr_band'],
            'borrower_type':r['borrower_type'],
            'property_type':r['property_type'],
            'employment':   r['employment_type'],
            'bucket':       r['arrears_bucket'],
            'days':         int(r['days_in_arrears']),
            'amount':       float(r['arrears_amount']),
            'loan_amt':     float(r['loan_amount']),
        })

claims = []
with open(CLAIMS_FILE, encoding='utf-8') as f:
    for r in csv.DictReader(f):
        claims.append({
            'claim_id':     r['claim_id'],
            'state':        r['state'],
            'lvr_band':     r['lvr_band'],
            'borrower_type':r['borrower_type'],
            'claim_amt':    float(r['claim_amount']),
            'recovery':     float(r['recovery_amount']),
            'net_loss':     float(r['net_loss']),
            'status':       r['claim_status'],
        })

# == Aggregations ==============================================================
LVR_BANDS  = ['≤80%','80-85%','85-90%','90-95%','95%+']
STATES     = ['NSW','VIC','QLD','WA','SA','TAS','ACT','NT']
BORR_TYPES = ['First Home Buyer','Owner Occupier','Investor','Refinancer']
PROP_TYPES = ['House','Apartment','Townhouse','Land']
EMP_TYPES  = ['PAYG','Self-Employed','Contract']
BUCKETS    = ['30','60','90','90+']

# Unique months in chronological order
all_dates_sorted = sorted(set(r['date'] for r in arrears))
date_to_month = {r['date']: r['month'] for r in arrears}
seen, month_entries = set(), []
for d in all_dates_sorted:
    m = date_to_month[d]
    if m not in seen:
        seen.add(m)
        month_entries.append((d, m))
month_dates  = [x[0] for x in month_entries]
month_labels = [x[1] for x in month_entries]

# Monthly arrears by bucket (for trend chart)
def monthly_bucket(bucket):
    counts = []
    for d in month_dates:
        n = sum(1 for r in arrears if r['date']==d and r['bucket']==bucket)
        counts.append(n)
    return counts

m30  = monthly_bucket('30')
m60  = monthly_bucket('60')
m90  = monthly_bucket('90')
m90p = monthly_bucket('90+')
m_total = [a+b+c+d for a,b,c,d in zip(m30,m60,m90,m90p)]

# National arrears rate per month (arrears count / eligible pool)
POOL = len(loans)
m_rate = [round(t/POOL*100,2) for t in m_total]
m90p_rate = [round(n/POOL*100,2) for n in m90p]

# KPIs
total_in_arrears = len(set(r['loan_id'] for r in arrears if r['date']==month_dates[-1]))
rate_30d  = sum(1 for r in arrears if r['date']==month_dates[-1] and r['bucket']=='30') / POOL * 100
rate_90p  = sum(1 for r in arrears if r['date']==month_dates[-1] and r['bucket']=='90+') / POOL * 100
total_claims = len(claims)
net_loss_total = sum(r['net_loss'] for r in claims)
default_count = sum(1 for r in loans if r['status'] in ('Default','Claim Paid'))
default_rate  = default_count / len(loans) * 100

# Default rate by LVR Band
def_by_lvr   = [sum(1 for r in loans if r['lvr_band']==b and r['status'] in ('Default','Claim Paid')) for b in LVR_BANDS]
total_by_lvr = [sum(1 for r in loans if r['lvr_band']==b) for b in LVR_BANDS]
dr_by_lvr    = [round(d/t*100,2) if t else 0 for d,t in zip(def_by_lvr,total_by_lvr)]

# Default rate by Borrower Type
def_by_borr   = [sum(1 for r in loans if r['borrower_type']==b and r['status'] in ('Default','Claim Paid')) for b in BORR_TYPES]
total_by_borr = [sum(1 for r in loans if r['borrower_type']==b) for b in BORR_TYPES]
dr_by_borr    = [round(d/t*100,2) if t else 0 for d,t in zip(def_by_borr,total_by_borr)]

# Default rate by Property Type
def_by_prop   = [sum(1 for r in loans if r['property_type']==p and r['status'] in ('Default','Claim Paid')) for p in PROP_TYPES]
total_by_prop = [sum(1 for r in loans if r['property_type']==p) for p in PROP_TYPES]
dr_by_prop    = [round(d/t*100,2) if t else 0 for d,t in zip(def_by_prop,total_by_prop)]

# Default rate by Employment Type
def_by_emp   = [sum(1 for r in loans if r['employment']==e and r['status'] in ('Default','Claim Paid')) for e in EMP_TYPES]
total_by_emp = [sum(1 for r in loans if r['employment']==e) for e in EMP_TYPES]
dr_by_emp    = [round(d/t*100,2) if t else 0 for d,t in zip(def_by_emp,total_by_emp)]

# State arrears rate (latest month) vs national avg
state_arr_rate = []
nat_avg = m_rate[-1]
for s in STATES:
    n = sum(1 for r in arrears if r['date']==month_dates[-1] and r['state']==s)
    pool_s = sum(1 for r in loans if r['state']==s)
    state_arr_rate.append(round(n/pool_s*100,2) if pool_s else 0)

# 90+ day trend for early warning (last 12 months)
ew_labels = month_labels[-12:]
ew_data   = m90p_rate[-12:]
THRESHOLD = 1.5   # 90+ day rate threshold

# Claims by state
claim_by_state = {s: sum(1 for c in claims if c['state']==s) for s in STATES}
loss_by_state  = {s: round(sum(c['net_loss'] for c in claims if c['state']==s)/1e3) for s in STATES}

def fm(n): return f"${n/1e6:.2f}M" if n>=1e6 else f"${n/1e3:.0f}K"

# == Tableau-style quick-filter cards (left rail) ==============================
def _fcard(label, group, options):
    opts  = f'<span class="fopt active" data-group="{group}" data-val=""><i class="bx"></i>(All)</span>'
    opts += ''.join(f'<span class="fopt" data-group="{group}" data-val="{o}"><i class="bx"></i>{o}</span>' for o in options)
    return (f'<div class="fcard"><div class="fcard-h">{label}<span class="x">&#9662;</span></div>'
            f'<div class="fopts">{opts}</div></div>')

filters_html = (_fcard('State','state',STATES)
              + _fcard('LVR Band','lvr_band',LVR_BANDS)
              + _fcard('Borrower Type','borrower_type',BORR_TYPES))

alert_html = ('<div class="annot warn"><span class="annot-i">&#9650;</span>'
              '<div><strong>Early warning &mdash; serious arrears.</strong> The 90+ day arrears rate peaked at '
              f'{max(m90p_rate):.2f}% in mid-2023 during the RBA rate-hike cycle &mdash; above the 1.5% internal '
              'threshold. The rate has since moderated but remains elevated versus pre-2022 levels. Monitor the '
              '85&ndash;95% LVR cohort closely.</div></div>') if max(m90p_rate) > THRESHOLD else ''

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>LMI Arrears &amp; Default Monitoring</title>
<link href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
*{{box-sizing:border-box;margin:0;padding:0;}}
body{{background:#ffffff;color:#333333;font-size:13px;
  font-family:'Open Sans','Benton Sans','Segoe UI',Arial,Helvetica,sans-serif;}}

/* Worksheet tab strip (Tableau) */
.tabstrip{{display:flex;align-items:flex-end;gap:2px;background:#e9e9e9;
  border-bottom:1px solid #c4c4c4;padding:0 10px;height:33px;}}
.tab{{font-size:12px;color:#5a5a5a;padding:6px 18px;border:1px solid transparent;
  border-bottom:none;background:#dcdcdc;border-radius:2px 2px 0 0;margin-bottom:-1px;
  text-decoration:none;cursor:pointer;}}
a.tab:hover{{background:#eaeaea;color:#1f1f1f;}}
.tab.active{{background:#ffffff;color:#1f1f1f;font-weight:700;
  border:1px solid #c4c4c4;border-bottom:1px solid #ffffff;}}
.tab.plus{{background:transparent;color:#9a9a9a;padding:6px 10px;}}

/* Title band */
.titlebar{{display:flex;align-items:flex-start;justify-content:space-between;gap:24px;
  padding:14px 22px 13px;border-bottom:1px solid #d6d6d6;background:#ffffff;}}
.titlebar h1{{font-size:20px;font-weight:700;color:#1f1f1f;letter-spacing:-0.01em;}}
.titlebar .sub{{font-size:11.5px;color:#888;margin-top:3px;}}
.asof{{text-align:right;font-size:10px;color:#8a8a8a;letter-spacing:0.04em;
  text-transform:uppercase;white-space:nowrap;}}
.asof .v{{font-size:17px;font-weight:700;color:#333;text-transform:none;letter-spacing:0;margin:2px 0;}}

/* KPI band (Tableau BANs) */
.kpi-row{{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;
  padding:13px 22px;background:#f4f4f4;border-bottom:1px solid #d6d6d6;}}
.kpi{{background:#ffffff;border:1px solid #d6d6d6;padding:11px 14px;border-top:3px solid #bcbcbc;}}
.kpi-val{{font-size:25px;font-weight:700;line-height:1.05;color:#2b2b2b;}}
.kpi-lbl{{font-size:11px;color:#5a5a5a;margin-top:4px;font-weight:600;}}
.kpi-note{{font-size:10px;color:#9a9a9a;margin-top:2px;}}
.kpi.c1{{border-top-color:#F28E2B;}} .kpi.c1 .kpi-val{{color:#C56A12;}}
.kpi.c2{{border-top-color:#E15759;}} .kpi.c2 .kpi-val{{color:#C0413F;}}
.kpi.c3{{border-top-color:#B0413E;}} .kpi.c3 .kpi-val{{color:#9A2F2C;}}
.kpi.c4{{border-top-color:#EDC948;}} .kpi.c4 .kpi-val{{color:#B7942B;}}
.kpi.c5{{border-top-color:#59A14F;}} .kpi.c5 .kpi-val{{color:#3F7A37;}}

/* Layout: left quick-filter rail + worksheet area */
.layout{{display:flex;align-items:stretch;min-height:62vh;}}
.filters{{width:216px;flex-shrink:0;background:#f4f4f4;border-right:1px solid #d6d6d6;padding:14px 12px;}}
.filters-h{{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:0.09em;
  color:#7a7a7a;margin-bottom:11px;padding-bottom:6px;border-bottom:1px solid #dadada;}}
.fcard{{background:#ffffff;border:1px solid #d6d6d6;margin-bottom:11px;}}
.fcard-h{{font-size:11px;font-weight:700;color:#4e4e4e;padding:6px 9px;
  border-bottom:1px solid #e6e6e6;background:#fafafa;display:flex;
  align-items:center;justify-content:space-between;}}
.fcard-h .x{{color:#a6a6a6;font-size:10px;}}
.fopts{{padding:7px 8px;display:flex;flex-wrap:wrap;gap:5px;}}
.fopt{{display:inline-flex;align-items:center;gap:6px;font-size:11px;color:#555;
  cursor:pointer;padding:3px 8px;border:1px solid #d3d3d3;border-radius:2px;
  background:#ffffff;user-select:none;transition:all .12s;}}
.fopt:hover{{border-color:#9bb9d9;}}
.fopt i.bx{{width:11px;height:11px;border:1px solid #9a9a9a;border-radius:2px;display:inline-block;flex-shrink:0;}}
.fopt.active{{background:#4576b5;border-color:#4576b5;color:#ffffff;}}
.fopt.active i.bx{{background:#ffffff;border-color:#ffffff;}}

.main{{flex:1;min-width:0;padding:16px 18px 46px;background:#ffffff;}}

/* Text / annotation tiles (Tableau text objects) */
.annot{{display:flex;gap:10px;align-items:flex-start;background:#ffffff;
  border:1px solid #d6d6d6;border-left:4px solid #9aa0a6;padding:11px 14px;
  margin-bottom:14px;font-size:12px;color:#555;line-height:1.6;}}
.annot strong{{color:#2b2b2b;}}
.annot-i{{color:#9aa0a6;font-size:13px;line-height:1.3;flex-shrink:0;}}
.annot.warn{{border-left-color:#E15759;background:#fdf3f3;}}
.annot.warn .annot-i{{color:#E15759;}}
.annot.info{{border-left-color:#4E79A7;background:#f5f8fb;}}
.annot.info .annot-i{{color:#4E79A7;}}

/* Section labels */
.sec{{font-size:10px;font-weight:700;letter-spacing:0.08em;color:#8a8a8a;
  text-transform:uppercase;margin:16px 0 9px;padding-bottom:5px;border-bottom:1px solid #e4e4e4;}}
.sec:first-child{{margin-top:2px;}}

/* Worksheet tiles */
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px;}}
.grid3{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-bottom:12px;}}
.mb{{margin-bottom:12px;}}
.card{{background:#ffffff;border:1px solid #d6d6d6;}}
.card.alert-card{{border-color:#e9b3b3;}}
.card-cap{{padding:8px 12px 7px;border-bottom:1px solid #ececec;background:#ffffff;}}
.card-title{{font-size:13px;font-weight:700;color:#2b2b2b;}}
.card-sub{{font-size:10.5px;color:#8f8f8f;margin-top:3px;line-height:1.5;}}
.card-body{{padding:12px 12px 10px;}}
.ch200{{position:relative;height:200px;}} .ch240{{position:relative;height:240px;}}
.ch280{{position:relative;height:280px;}} .ch320{{position:relative;height:320px;}}

/* Crosstab summary */
.stat-blocks{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:12px;}}
.stat-block{{background:#ffffff;border:1px solid #d6d6d6;padding:14px 16px;}}
.sb-val{{font-size:23px;font-weight:700;color:#2b2b2b;}}
.sb-lbl{{font-size:11px;color:#5a5a5a;margin-top:4px;font-weight:600;}}
.sb-sub{{font-size:10px;color:#9a9a9a;margin-top:2px;}}

/* Status / data-source bar */
.footer{{display:flex;align-items:center;justify-content:space-between;
  padding:8px 22px;font-size:10.5px;color:#8a8a8a;background:#f4f4f4;border-top:1px solid #d6d6d6;}}
.footer .ds::before{{content:'';display:inline-block;width:8px;height:8px;border-radius:50%;
  background:#59A14F;margin-right:6px;vertical-align:middle;}}
</style>
</head>
<body>

<div class="tabstrip">
  <div class="tab active">Arrears &amp; Default</div>
  <a class="tab" href="portfolio_risk_dashboard.html">Portfolio Risk</a>
  <div class="tab plus">+</div>
</div>

<div class="titlebar">
  <div>
    <h1>LMI Arrears &amp; Default Monitoring</h1>
    <div class="sub">Lenders Mortgage Insurance &middot; 30 / 60 / 90 day arrears &middot; default analysis &middot; early-warning indicators &middot; Jan 2022 &ndash; Dec 2024</div>
  </div>
  <div class="asof">
    <div>Reporting period</div>
    <div class="v">Dec 2024</div>
    <div>36 monthly snapshots</div>
  </div>
</div>

<div class="kpi-row">
  <div class="kpi c1"><div class="kpi-val">{total_in_arrears:,}</div><div class="kpi-lbl">In Arrears (Latest Month)</div><div class="kpi-note">{total_in_arrears/POOL*100:.1f}% of portfolio</div></div>
  <div class="kpi c2"><div class="kpi-val">{rate_30d:.2f}%</div><div class="kpi-lbl">30-Day Arrears Rate</div><div class="kpi-note">Latest month</div></div>
  <div class="kpi c3"><div class="kpi-val">{rate_90p:.2f}%</div><div class="kpi-lbl">90+ Day Arrears Rate</div><div class="kpi-note">Serious arrears &mdash; default risk</div></div>
  <div class="kpi c4"><div class="kpi-val">{total_claims}</div><div class="kpi-lbl">Claims Lodged</div><div class="kpi-note">{default_rate:.1f}% default rate</div></div>
  <div class="kpi c5"><div class="kpi-val">{fm(net_loss_total)}</div><div class="kpi-lbl">Net Loss After Recovery</div><div class="kpi-note">Claims paid less recoveries</div></div>
</div>

<div class="layout">
  <aside class="filters">
    <div class="filters-h">Filters</div>
    {filters_html}
  </aside>

  <main class="main">

    {alert_html}

    <div class="annot info">
      <span class="annot-i">&#9632;</span>
      <div>
        <strong>Arrears trend &mdash; rate-hike stress cycle visible in 2022&ndash;2023.</strong>
        Peak arrears stress occurred in <strong>mid-2023</strong> as the RBA rate-hike cycle (May 2022 &ndash; Nov 2023) compressed borrower serviceability.
        The <strong>90+ day rate peaked at {max(m90p_rate):.2f}%</strong> before moderating into 2024.
        High-LVR borrowers (90&ndash;95% and 95%+) show roughly <strong>3&times; the default rate</strong> of lower-LVR cohorts,
        and self-employed borrowers carry elevated default risk versus PAYG.
      </div>
    </div>

    <div class="sec">Monthly Arrears Trend &middot; Jan 2022 &ndash; Dec 2024</div>
    <div class="card mb">
      <div class="card-cap">
        <div class="card-title">Arrears Rate Over Time &mdash; 30 / 60 / 90 / 90+ Day</div>
        <div class="card-sub">Monthly percentage of the portfolio in each arrears bucket. The 2022&ndash;2023 rate-hike cycle is clearly visible as a rising arrears tide. The 90+ day band is the primary leading indicator of incoming claims.</div>
      </div>
      <div class="card-body"><div class="ch280"><canvas id="trendChart"></canvas></div></div>
    </div>

    <div class="sec">Arrears Volume by Bucket &middot; Stacked</div>
    <div class="card mb">
      <div class="card-cap">
        <div class="card-title">Monthly Arrears Count by Severity Bucket (Stacked)</div>
        <div class="card-sub">A growing 90+ band (purple) without a proportional increase in the 30-day band signals loans skipping intermediate stages &mdash; a sign of acute financial distress rather than short-term cash-flow issues.</div>
      </div>
      <div class="card-body"><div class="ch280"><canvas id="stackedChart"></canvas></div></div>
    </div>

    <div class="sec">Default Rate Analysis &middot; By Risk Segment</div>
    <div class="grid3 mb">
      <div class="card">
        <div class="card-cap"><div class="card-title">Default Rate by LVR Band</div>
          <div class="card-sub">The sharpest risk gradient in LMI portfolios. Each 5-point LVR step materially increases default probability.</div></div>
        <div class="card-body"><div class="ch240"><canvas id="drLvrChart"></canvas></div></div>
      </div>
      <div class="card">
        <div class="card-cap"><div class="card-title">Default Rate by Borrower Type</div>
          <div class="card-sub">Investors show higher default rates than owner-occupiers &mdash; investment properties are more likely to be sold or defaulted on when cash flow deteriorates.</div></div>
        <div class="card-body"><div class="ch240"><canvas id="drBorrChart"></canvas></div></div>
      </div>
      <div class="card">
        <div class="card-cap"><div class="card-title">Default Rate by Property Type</div>
          <div class="card-sub">Apartments and land carry higher default rates. Land loans lack income-generating capacity; apartments face oversupply risk that depresses recoveries.</div></div>
        <div class="card-body"><div class="ch240"><canvas id="drPropChart"></canvas></div></div>
      </div>
    </div>

    <div class="sec">Employment Risk &middot; State vs National Benchmark</div>
    <div class="grid2 mb">
      <div class="card">
        <div class="card-cap"><div class="card-title">Default Rate by Employment Type</div>
          <div class="card-sub">Self-employed borrowers carry the highest default risk &mdash; income volatility, irregular cash flows, and greater economic-cycle exposure. Contract workers sit between PAYG and self-employed.</div></div>
        <div class="card-body"><div class="ch240"><canvas id="drEmpChart"></canvas></div></div>
      </div>
      <div class="card">
        <div class="card-cap"><div class="card-title">State Arrears Rate vs National Average (Latest Month)</div>
          <div class="card-sub">States above the national-average reference line are experiencing above-average arrears stress. NT consistently shows elevated arrears due to the smaller, more volatile local economy.</div></div>
        <div class="card-body"><div class="ch240"><canvas id="stateArrChart"></canvas></div></div>
      </div>
    </div>

    <div class="sec">Early-Warning Indicator &middot; 90+ Day Arrears Rate &mdash; Last 12 Months</div>
    <div class="card alert-card mb">
      <div class="card-cap"><div class="card-title">90+ Day Arrears Rate &mdash; Trend vs Threshold (1.5%)</div>
        <div class="card-sub">The 90+ day rate is the leading indicator for incoming claims. When it breaches the 1.5% threshold (reference line), claims typically follow within 3&ndash;6 months. Monitor monthly for threshold crossings.</div></div>
      <div class="card-body"><div class="ch240"><canvas id="ewChart"></canvas></div></div>
    </div>

    <div class="sec">Claims Summary</div>
    <div class="stat-blocks">
      <div class="stat-block"><div class="sb-val" style="color:#C0413F;">{total_claims}</div><div class="sb-lbl">Total Claims Lodged</div><div class="sb-sub">{default_rate:.2f}% of portfolio</div></div>
      <div class="stat-block"><div class="sb-val" style="color:#C56A12;">{fm(sum(c['claim_amt'] for c in claims))}</div><div class="sb-lbl">Gross Claims Amount</div><div class="sb-sub">Before recoveries</div></div>
      <div class="stat-block"><div class="sb-val" style="color:#3F7A37;">{fm(sum(c['recovery'] for c in claims))}</div><div class="sb-lbl">Total Recoveries</div><div class="sb-sub">From property sales</div></div>
      <div class="stat-block"><div class="sb-val" style="color:#9A2F2C;">{fm(net_loss_total)}</div><div class="sb-lbl">Net Loss After Recovery</div><div class="sb-sub">Actual cost to insurer</div></div>
    </div>

  </main>
</div>

<div class="footer">
  <div class="ds">Data source: LMI loan, arrears &amp; claims extract (synthetic demonstration data)</div>
  <div>{POOL:,} policies &middot; {len(arrears):,} arrears snapshots &middot; Tableau Public style</div>
</div>

<script>
const T_BLUE='#4E79A7',T_ORANGE='#F28E2B',T_RED='#E15759',T_TEAL='#76B7B2',
      T_GREEN='#59A14F',T_YELLOW='#EDC948',T_PURPLE='#B07AA1',T_BROWN='#9C755F',T_GRAY='#9aa0a6';
const GRID='#e8e8e8', AXIS='#cccccc', TICK='#707070';
Chart.defaults.color=TICK;
Chart.defaults.font.family="'Open Sans','Benton Sans',Arial,sans-serif";
Chart.defaults.font.size=11;
Chart.defaults.plugins.legend.labels.boxWidth=10;
Chart.defaults.plugins.legend.labels.padding=10;
Chart.defaults.plugins.legend.labels.color='#4e4e4e';
function hexA(hex,a){{const n=parseInt(hex.slice(1),16);return `rgba(${{n>>16&255}},${{n>>8&255}},${{n&255}},${{a}})`;}}
function risk(v,hi,mid){{return v>hi?T_RED:v>mid?T_ORANGE:T_GREEN;}}
const xAxis=(extra={{}})=>Object.assign({{grid:{{display:false}},border:{{color:AXIS}},ticks:{{color:TICK}}}},extra);
const yAxis=(extra={{}})=>Object.assign({{grid:{{color:GRID}},border:{{display:false}},ticks:{{color:TICK}}}},extra);

const MONTHS = {json.dumps(month_labels)};
const M30    = {json.dumps(m30)};
const M60    = {json.dumps(m60)};
const M90    = {json.dumps(m90)};
const M90P   = {json.dumps(m90p)};
const MRATE  = {json.dumps(m_rate)};
const M90PRATE = {json.dumps(m90p_rate)};
const POOL = {POOL};

// Trend chart
new Chart(document.getElementById('trendChart'),{{type:'line',
  data:{{labels:MONTHS,datasets:[
    {{label:'30-Day %',data:MRATE.map((_,i)=>M30[i]/POOL*100),borderColor:T_BLUE,backgroundColor:hexA(T_BLUE,0.07),tension:0,borderWidth:1.5,pointRadius:0,fill:true}},
    {{label:'60-Day %',data:MRATE.map((_,i)=>M60[i]/POOL*100),borderColor:T_ORANGE,backgroundColor:hexA(T_ORANGE,0.06),tension:0,borderWidth:1.5,pointRadius:0,fill:true}},
    {{label:'90-Day %',data:MRATE.map((_,i)=>M90[i]/POOL*100),borderColor:T_RED,backgroundColor:hexA(T_RED,0.05),tension:0,borderWidth:1.5,pointRadius:0,fill:true}},
    {{label:'90+ Day %',data:M90PRATE,borderColor:T_PURPLE,backgroundColor:hexA(T_PURPLE,0.10),tension:0,borderWidth:2.5,pointRadius:0,fill:true}},
  ]}},
  options:{{plugins:{{legend:{{position:'top'}},tooltip:{{mode:'index',intersect:false,callbacks:{{label:c=>c.dataset.label+': '+c.parsed.y.toFixed(2)+'%'}}}}}},
    scales:{{y:yAxis({{beginAtZero:true,ticks:{{color:TICK,callback:v=>v.toFixed(1)+'%'}}}}),x:xAxis({{ticks:{{color:TICK,maxTicksLimit:12}}}})}}
  }}}});

new Chart(document.getElementById('stackedChart'),{{type:'bar',
  data:{{labels:MONTHS,datasets:[
    {{label:'30 Day',data:M30,backgroundColor:T_BLUE,borderWidth:0}},
    {{label:'60 Day',data:M60,backgroundColor:T_ORANGE,borderWidth:0}},
    {{label:'90 Day',data:M90,backgroundColor:T_RED,borderWidth:0}},
    {{label:'90+ Day',data:M90P,backgroundColor:T_PURPLE,borderWidth:0}},
  ]}},
  options:{{plugins:{{legend:{{position:'top'}},tooltip:{{mode:'index',intersect:false}}}},
    scales:{{x:Object.assign(xAxis({{ticks:{{color:TICK,maxTicksLimit:12}}}}),{{stacked:true}}),
      y:Object.assign(yAxis({{beginAtZero:true}}),{{stacked:true}})}}
  }}}});

new Chart(document.getElementById('drLvrChart'),{{type:'bar',
  data:{{labels:{json.dumps(LVR_BANDS)},datasets:[{{label:'Default Rate %',
    data:{json.dumps(dr_by_lvr)},
    backgroundColor:{json.dumps(dr_by_lvr)}.map(v=>risk(v,4,2)),borderWidth:0}}]}},
  options:{{plugins:{{legend:{{display:false}},tooltip:{{callbacks:{{label:c=>c.parsed.y.toFixed(2)+'% default rate'}}}}}},
    scales:{{y:yAxis({{beginAtZero:true,ticks:{{color:TICK,callback:v=>v+'%'}}}}),x:xAxis()}}
  }}}});

new Chart(document.getElementById('drBorrChart'),{{type:'bar',
  data:{{labels:{json.dumps(BORR_TYPES)},datasets:[{{label:'Default Rate %',
    data:{json.dumps(dr_by_borr)},
    backgroundColor:{json.dumps(dr_by_borr)}.map(v=>risk(v,4,2)),borderWidth:0}}]}},
  options:{{plugins:{{legend:{{display:false}},tooltip:{{callbacks:{{label:c=>c.parsed.y.toFixed(2)+'% default rate'}}}}}},
    scales:{{y:yAxis({{beginAtZero:true,ticks:{{color:TICK,callback:v=>v+'%'}}}}),x:xAxis({{ticks:{{color:TICK,font:{{size:10}}}}}})}}
  }}}});

new Chart(document.getElementById('drPropChart'),{{type:'bar',
  data:{{labels:{json.dumps(PROP_TYPES)},datasets:[{{label:'Default Rate %',
    data:{json.dumps(dr_by_prop)},
    backgroundColor:{json.dumps(dr_by_prop)}.map(v=>risk(v,4,2)),borderWidth:0}}]}},
  options:{{plugins:{{legend:{{display:false}},tooltip:{{callbacks:{{label:c=>c.parsed.y.toFixed(2)+'% default rate'}}}}}},
    scales:{{y:yAxis({{beginAtZero:true,ticks:{{color:TICK,callback:v=>v+'%'}}}}),x:xAxis()}}
  }}}});

new Chart(document.getElementById('drEmpChart'),{{type:'bar',
  data:{{labels:{json.dumps(EMP_TYPES)},datasets:[{{label:'Default Rate %',
    data:{json.dumps(dr_by_emp)},
    backgroundColor:[T_GREEN,T_RED,T_ORANGE],borderWidth:0}}]}},
  options:{{plugins:{{legend:{{display:false}},tooltip:{{callbacks:{{label:c=>c.parsed.y.toFixed(2)+'% default rate'}}}}}},
    scales:{{y:yAxis({{beginAtZero:true,ticks:{{color:TICK,callback:v=>v+'%'}}}}),x:xAxis()}}
  }}}});

const natAvg = {nat_avg};
new Chart(document.getElementById('stateArrChart'),{{type:'bar',
  data:{{labels:{json.dumps(STATES)},datasets:[
    {{label:'State Rate %',data:{json.dumps(state_arr_rate)},
      backgroundColor:{json.dumps(state_arr_rate)}.map(v=>v>natAvg?T_RED:T_BLUE),borderWidth:0}},
    {{label:'National Avg',data:Array({len(STATES)}).fill(natAvg),type:'line',
      borderColor:T_GRAY,borderDash:[5,4],borderWidth:2,pointRadius:0,fill:false}}
  ]}},
  options:{{indexAxis:'y',plugins:{{legend:{{position:'top'}},
    tooltip:{{callbacks:{{label:c=>c.dataset.label+': '+c.parsed.x.toFixed(2)+'%'}}}}}},
    scales:{{x:Object.assign(yAxis({{ticks:{{color:TICK,callback:v=>v+'%'}}}}),{{grid:{{color:GRID}}}}),y:xAxis()}}
  }}}});

const EW_LABELS = {json.dumps(ew_labels)};
const EW_DATA   = {json.dumps(ew_data)};
const THRESH    = {THRESHOLD};
new Chart(document.getElementById('ewChart'),{{type:'line',
  data:{{labels:EW_LABELS,datasets:[
    {{label:'90+ Day Rate %',data:EW_DATA,
      borderColor:T_RED,backgroundColor:hexA(T_RED,0.08),
      tension:0,borderWidth:2.5,pointRadius:4,pointBackgroundColor:EW_DATA.map(v=>v>THRESH?T_RED:T_GREEN),fill:true}},
    {{label:'Threshold (1.5%)',data:Array(EW_LABELS.length).fill(THRESH),type:'line',
      borderColor:T_GRAY,borderDash:[6,4],borderWidth:2,pointRadius:0,fill:false}}
  ]}},
  options:{{plugins:{{legend:{{position:'top'}},
    tooltip:{{callbacks:{{label:c=>c.dataset.label+': '+c.parsed.y.toFixed(2)+'%'}}}}}},
    scales:{{y:yAxis({{ticks:{{color:TICK,callback:v=>v.toFixed(1)+'%'}}}}),x:xAxis()}}
  }}}});

// Quick-filter cards (visual selection, Tableau-style)
document.querySelectorAll('.fopt').forEach(p=>{{
  p.addEventListener('click',()=>{{
    const g=p.dataset.group;
    document.querySelectorAll(`.fopt[data-group="${{g}}"]`).forEach(x=>x.classList.remove('active'));
    p.classList.add('active');
  }});
}});
</script>
</body>
</html>"""

with open(OUT,'w',encoding='utf-8') as f:
    f.write(html)
print(f"Written: {OUT}  ({len(html):,} chars)")
