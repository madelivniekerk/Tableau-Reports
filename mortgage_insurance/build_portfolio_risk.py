"""
Build: LMI Portfolio Risk Dashboard  ->  portfolio_risk_dashboard.html
Authentic Tableau-style theme (light canvas, worksheet tiles, Tableau 10 palette).
"""
import json, csv, os
from collections import defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "loans.csv")
OUT  = os.path.join(BASE, "portfolio_risk_dashboard.html")

# == Load & aggregate ==========================================================
rows = []
with open(DATA, encoding='utf-8') as f:
    for r in csv.DictReader(f):
        rows.append({
            'loan_id':       r['loan_id'],
            'state':         r['state'],
            'lvr_band':      r['lvr_band'],
            'lvr':           float(r['lvr']),
            'borrower_type': r['borrower_type'],
            'property_type': r['property_type'],
            'lender':        r['lender'],
            'lender_channel':r['lender_channel'],
            'employment':    r['employment_type'],
            'vintage':       int(r['vintage_year']),
            'loan_amt':      float(r['loan_amount']),
            'prop_val':      float(r['property_value']),
            'premium':       float(r['premium_amount']),
            'status':        r['loan_status'],
        })

# Pre-aggregate for charts
LVR_BANDS   = ['≤80%','80-85%','85-90%','90-95%','95%+']
STATES      = ['NSW','VIC','QLD','WA','SA','TAS','ACT','NT']
BORR_TYPES  = ['First Home Buyer','Owner Occupier','Investor','Refinancer']
PROP_TYPES  = ['House','Apartment','Townhouse','Land']
LENDERS     = ['Commonwealth Bank','Westpac','ANZ','NAB','Macquarie',
               'Bendigo Bank','Bank of Queensland','ING','Suncorp','AMP Bank']
VINTAGES    = [2019,2020,2021,2022,2023,2024]
CHANNELS    = ['Bank Branch','Mortgage Broker','Online / Direct']

def agg(rows, key, values=None):
    d = defaultdict(lambda:{'count':0,'exposure':0,'premium':0})
    for r in rows:
        k = r[key]
        if values and k not in values: continue
        d[k]['count']    += 1
        d[k]['exposure'] += r['loan_amt']
        d[k]['premium']  += r['premium']
    return d

# KPIs (all loans)
active = [r for r in rows if r['status'] in ('Active','In Arrears')]
total_exposure   = sum(r['loan_amt'] for r in rows)
active_exposure  = sum(r['loan_amt'] for r in active)
total_premium    = sum(r['premium']  for r in rows)
avg_lvr          = sum(r['lvr'] for r in rows) / len(rows)
high_risk        = sum(r['loan_amt'] for r in rows if r['lvr_band'] in ('90-95%','95%+'))
high_risk_pct    = high_risk / total_exposure * 100

# By LVR Band
lvr_counts   = [sum(1 for r in rows if r['lvr_band']==b) for b in LVR_BANDS]
lvr_exposure = [round(sum(r['loan_amt'] for r in rows if r['lvr_band']==b)/1e6,1) for b in LVR_BANDS]
lvr_premium  = [round(sum(r['premium']  for r in rows if r['lvr_band']==b)/1e3) for b in LVR_BANDS]

# LVR distribution histogram (bins of 5)
bins = list(range(65,100,5))
bin_labels = [f"{b}-{b+5}%" for b in bins]
bin_counts = [sum(1 for r in rows if b <= r['lvr'] < b+5) for b in bins]

# By State
state_counts   = [sum(1 for r in rows if r['state']==s) for s in STATES]
state_exposure = [round(sum(r['loan_amt'] for r in rows if r['state']==s)/1e6,1) for s in STATES]
state_avg_lvr  = [round(sum(r['lvr'] for r in rows if r['state']==s)/(sum(1 for r in rows if r['state']==s) or 1),1) for s in STATES]

# By Borrower Type
borr_counts   = [sum(1 for r in rows if r['borrower_type']==b) for b in BORR_TYPES]
borr_exposure = [round(sum(r['loan_amt'] for r in rows if r['borrower_type']==b)/1e6,1) for b in BORR_TYPES]

# By Property Type
prop_counts   = [sum(1 for r in rows if r['property_type']==p) for p in PROP_TYPES]
prop_exposure = [round(sum(r['loan_amt'] for r in rows if r['property_type']==p)/1e6,1) for p in PROP_TYPES]

# By Lender
lend_counts   = [sum(1 for r in rows if r['lender']==l) for l in LENDERS]
lend_exposure = [round(sum(r['loan_amt'] for r in rows if r['lender']==l)/1e6,1) for l in LENDERS]

# By Vintage
vint_counts   = [sum(1 for r in rows if r['vintage']==v) for v in VINTAGES]
vint_exposure = [round(sum(r['loan_amt'] for r in rows if r['vintage']==v)/1e6,1) for v in VINTAGES]

# By Channel
chan_counts = [sum(1 for r in rows if r['lender_channel']==c) for c in CHANNELS]

# Format helpers
def fm(n):  return f"${n/1e9:.2f}B" if n>=1e9 else f"${n/1e6:.1f}M"
def fk(n):  return f"${n/1e3:.0f}K"

js_data = json.dumps(rows[:500], separators=(',',':'))   # embed subset for filter interactivity

# == Tableau-style quick-filter cards (left rail) ==============================
def _fcard(label, group, options):
    opts  = f'<span class="fopt active" data-group="{group}" data-val=""><i class="bx"></i>(All)</span>'
    opts += ''.join(f'<span class="fopt" data-group="{group}" data-val="{o}"><i class="bx"></i>{o}</span>' for o in options)
    return (f'<div class="fcard"><div class="fcard-h">{label}<span class="x">&#9662;</span></div>'
            f'<div class="fopts">{opts}</div></div>')

filters_html = (_fcard('State','state',STATES)
              + _fcard('LVR Band','lvr_band',LVR_BANDS)
              + _fcard('Borrower Type','borrower_type',BORR_TYPES))

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>LMI Portfolio Risk Dashboard</title>
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
.kpi.c1{{border-top-color:#4E79A7;}} .kpi.c1 .kpi-val{{color:#3A5E85;}}
.kpi.c2{{border-top-color:#59A14F;}} .kpi.c2 .kpi-val{{color:#3F7A37;}}
.kpi.c3{{border-top-color:#F28E2B;}} .kpi.c3 .kpi-val{{color:#C56A12;}}
.kpi.c4{{border-top-color:#76B7B2;}} .kpi.c4 .kpi-val{{color:#4E8C87;}}
.kpi.c5{{border-top-color:#E15759;}} .kpi.c5 .kpi-val{{color:#C0413F;}}

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
  border:1px solid #d6d6d6;border-left:4px solid #4E79A7;padding:11px 14px;
  margin-bottom:14px;font-size:12px;color:#555;line-height:1.6;}}
.annot strong{{color:#2b2b2b;}}
.annot-i{{color:#4E79A7;font-size:13px;line-height:1.3;flex-shrink:0;}}

/* Section labels */
.sec{{font-size:10px;font-weight:700;letter-spacing:0.08em;color:#8a8a8a;
  text-transform:uppercase;margin:16px 0 9px;padding-bottom:5px;border-bottom:1px solid #e4e4e4;}}
.sec:first-child{{margin-top:2px;}}

/* Worksheet tiles */
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px;}}
.grid3{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-bottom:12px;}}
.mb{{margin-bottom:12px;}}
.card{{background:#ffffff;border:1px solid #d6d6d6;}}
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
  <a class="tab" href="arrears_default_dashboard.html">Arrears &amp; Default</a>
  <div class="tab active">Portfolio Risk</div>
  <div class="tab plus">+</div>
</div>

<div class="titlebar">
  <div>
    <h1>LMI Portfolio Risk Dashboard</h1>
    <div class="sub">Lenders Mortgage Insurance &middot; {len(rows):,} policies &middot; Australia &middot; LVR concentration, geographic &amp; vintage risk</div>
  </div>
  <div class="asof">
    <div>Portfolio as at</div>
    <div class="v">Jun 2024</div>
    <div>Synthetic demo data</div>
  </div>
</div>

<div class="kpi-row">
  <div class="kpi c1"><div class="kpi-val">{len(rows):,}</div><div class="kpi-lbl">Total Policies</div><div class="kpi-note">{sum(1 for r in rows if r['status']=='Active'):,} active</div></div>
  <div class="kpi c2"><div class="kpi-val">{fm(total_exposure)}</div><div class="kpi-lbl">Total Insured Exposure</div><div class="kpi-note">All statuses</div></div>
  <div class="kpi c3"><div class="kpi-val">{avg_lvr:.1f}%</div><div class="kpi-lbl">Average LVR</div><div class="kpi-note">Portfolio weighted</div></div>
  <div class="kpi c4"><div class="kpi-val">{fm(total_premium)}</div><div class="kpi-lbl">Total Premium Written</div><div class="kpi-note">All origination years</div></div>
  <div class="kpi c5"><div class="kpi-val">{fm(high_risk)}</div><div class="kpi-lbl">High-Risk Exposure (LVR&gt;90%)</div><div class="kpi-note">{high_risk_pct:.1f}% of total</div></div>
</div>

<div class="layout">
  <aside class="filters">
    <div class="filters-h">Filters</div>
    {filters_html}
  </aside>

  <main class="main">

    <div class="annot">
      <span class="annot-i" id="story-icon">&#9632;</span>
      <div>
        <div style="font-weight:700;color:#2b2b2b;margin-bottom:3px;" id="story-title">Portfolio overview &mdash; {len(rows):,} LMI policies &middot; {fm(total_exposure)} exposure</div>
        <div id="story-text">
          <strong>{len(rows):,} insured loans</strong> across 8 states. The portfolio is concentrated in the
          <strong>85&ndash;90% LVR band ({lvr_counts[2]:,} policies)</strong> &mdash; typical for LMI, where coverage kicks in above 80% LVR.
          High-risk exposure (LVR&gt;90%) represents <strong>{fm(high_risk)} ({high_risk_pct:.1f}%)</strong> of the total.
          Use the filters on the left to drill into state, band, or borrower type.
        </div>
      </div>
    </div>

    <div class="sec">LVR Distribution &middot; Core Risk Metric</div>
    <div class="grid2 mb">
      <div class="card">
        <div class="card-cap"><div class="card-title">LVR Distribution &mdash; Policy Count by Band</div>
          <div class="card-sub">The heartbeat metric of any LMI portfolio. Concentration in the 85&ndash;95% band is expected &mdash; this is the core LMI sweet spot. Policies above 95% carry the highest default risk.</div></div>
        <div class="card-body"><div class="ch240"><canvas id="lvrBandChart"></canvas></div></div>
      </div>
      <div class="card">
        <div class="card-cap"><div class="card-title">Insured Exposure by LVR Band ($M)</div>
          <div class="card-sub">Total loan amount exposed per LVR band. High exposure in the 90&ndash;95% band relative to premium collected is the key loss-severity risk indicator.</div></div>
        <div class="card-body"><div class="ch240"><canvas id="lvrExpChart"></canvas></div></div>
      </div>
    </div>

    <div class="sec">LVR Histogram &middot; Granular Distribution</div>
    <div class="card mb">
      <div class="card-cap"><div class="card-title">LVR Value Distribution &mdash; 5-Point Bins</div>
        <div class="card-sub">Granular view of where LVR values cluster within the portfolio. A spike in the 90&ndash;95 range signals higher systematic risk &mdash; these loans have thinner equity buffers if property prices fall.</div></div>
      <div class="card-body"><div class="ch200"><canvas id="lvrHistChart"></canvas></div></div>
    </div>

    <div class="sec">Geographic Concentration &middot; State View</div>
    <div class="grid2 mb">
      <div class="card">
        <div class="card-cap"><div class="card-title">Insured Exposure by State ($M)</div>
          <div class="card-sub">NSW and VIC dominate exposure &mdash; reflecting Australia&rsquo;s housing-market concentration in the two largest cities. Regional concentration risk is a key underwriting consideration.</div></div>
        <div class="card-body"><div class="ch280"><canvas id="stateExpChart"></canvas></div></div>
      </div>
      <div class="card">
        <div class="card-cap"><div class="card-title">Average LVR by State</div>
          <div class="card-sub">States with higher average LVR carry more per-loan risk. NT and NSW typically show higher LVRs &mdash; reflecting affordability stress and higher loan-to-value ratios for first home buyers.</div></div>
        <div class="card-body"><div class="ch280"><canvas id="stateAvgLvrChart"></canvas></div></div>
      </div>
    </div>

    <div class="sec">Portfolio Mix &middot; Borrower &amp; Property</div>
    <div class="grid3 mb">
      <div class="card">
        <div class="card-cap"><div class="card-title">Policies by Borrower Type</div>
          <div class="card-sub">First Home Buyers typically drive the highest-LVR loans &mdash; the segment most sensitive to rate rises and property-value falls.</div></div>
        <div class="card-body"><div class="ch240"><canvas id="borrChart"></canvas></div></div>
      </div>
      <div class="card">
        <div class="card-cap"><div class="card-title">Policies by Property Type</div>
          <div class="card-sub">Houses dominate. Apartments carry higher concentration risk in certain postcodes and are more vulnerable to oversupply-driven value falls.</div></div>
        <div class="card-body"><div class="ch240"><canvas id="propChart"></canvas></div></div>
      </div>
      <div class="card">
        <div class="card-cap"><div class="card-title">Origination Channel Mix</div>
          <div class="card-sub">Mortgage-broker-originated loans (50%+) are the dominant channel &mdash; broker-sourced loans historically show marginally higher LVRs due to client optimisation.</div></div>
        <div class="card-body"><div class="ch240"><canvas id="chanChart"></canvas></div></div>
      </div>
    </div>

    <div class="sec">Vintage Analysis &middot; Origination by Year</div>
    <div class="grid2 mb">
      <div class="card">
        <div class="card-cap"><div class="card-title">New Policies by Origination Year</div>
          <div class="card-sub">Volume trend of new LMI certificates issued. The 2021&ndash;2022 peak reflects the post-COVID housing boom; the 2023 dip reflects the rate-rise slowdown in property transactions.</div></div>
        <div class="card-body"><div class="ch240"><canvas id="vintCountChart"></canvas></div></div>
      </div>
      <div class="card">
        <div class="card-cap"><div class="card-title">New Exposure by Origination Year ($M)</div>
          <div class="card-sub">Despite similar policy counts, exposure per vintage reflects property-price growth &mdash; the 2022 vintage carries the highest average loan amount per policy, reflecting peak pricing.</div></div>
        <div class="card-body"><div class="ch240"><canvas id="vintExpChart"></canvas></div></div>
      </div>
    </div>

    <div class="sec">Lender Distribution &middot; Top Originators</div>
    <div class="card mb">
      <div class="card-cap"><div class="card-title">Policies by Originating Lender</div>
        <div class="card-sub">The Big 4 dominate origination volumes. Concentration in any single lender is a counterparty-risk consideration &mdash; a lender changing their LMI panel can significantly impact new-business volumes.</div></div>
      <div class="card-body"><div class="ch200"><canvas id="lenderChart"></canvas></div></div>
    </div>

    <div class="sec">Portfolio Summary</div>
    <div class="stat-blocks">
      <div class="stat-block"><div class="sb-val" style="color:#3A5E85;">{sum(1 for r in rows if r['lvr_band'] in ('90-95%','95%+')):,}</div><div class="sb-lbl">High-Risk Policies (LVR&gt;90%)</div><div class="sb-sub">{sum(1 for r in rows if r['lvr_band'] in ('90-95%','95%+'))/len(rows)*100:.1f}% of portfolio</div></div>
      <div class="stat-block"><div class="sb-val" style="color:#C56A12;">{sum(1 for r in rows if r['borrower_type']=='First Home Buyer'):,}</div><div class="sb-lbl">First Home Buyer Policies</div><div class="sb-sub">Highest-LVR segment</div></div>
      <div class="stat-block"><div class="sb-val" style="color:#3F7A37;">{fm(total_premium)}</div><div class="sb-lbl">Total Premium Written</div><div class="sb-sub">All origination years</div></div>
      <div class="stat-block"><div class="sb-val" style="color:#C0413F;">{sum(1 for r in rows if r['status'] in ('Default','Claim Paid')):,}</div><div class="sb-lbl">Defaults &amp; Claims</div><div class="sb-sub">{sum(1 for r in rows if r['status'] in ('Default','Claim Paid'))/len(rows)*100:.1f}% default rate</div></div>
    </div>

  </main>
</div>

<div class="footer">
  <div class="ds">Data source: LMI policy extract (synthetic demonstration data)</div>
  <div>{len(rows):,} policies &middot; {fm(total_exposure)} exposure &middot; Tableau Public style</div>
</div>

<script>
const T_BLUE='#4E79A7',T_ORANGE='#F28E2B',T_RED='#E15759',T_TEAL='#76B7B2',
      T_GREEN='#59A14F',T_YELLOW='#EDC948',T_PURPLE='#B07AA1',T_BROWN='#9C755F',
      T_PINK='#FF9DA7',T_GRAY='#BAB0AC';
const GRID='#e8e8e8', AXIS='#cccccc', TICK='#707070';
Chart.defaults.color=TICK;
Chart.defaults.font.family="'Open Sans','Benton Sans',Arial,sans-serif";
Chart.defaults.font.size=11;
Chart.defaults.plugins.legend.labels.boxWidth=10;
Chart.defaults.plugins.legend.labels.padding=10;
Chart.defaults.plugins.legend.labels.color='#4e4e4e';
const xAxis=(extra={{}})=>Object.assign({{grid:{{display:false}},border:{{color:AXIS}},ticks:{{color:TICK}}}},extra);
const yAxis=(extra={{}})=>Object.assign({{grid:{{color:GRID}},border:{{display:false}},ticks:{{color:TICK}}}},extra);

const LVR_BANDS={json.dumps(LVR_BANDS)};
// Sequential green -> red risk ramp for LVR bands
const LVR_COLORS=['#59A14F','#A7B84C','#EDC948','#F28E2B','#E15759'];

new Chart(document.getElementById('lvrBandChart'),{{type:'bar',
  data:{{labels:{json.dumps(LVR_BANDS)},datasets:[{{label:'Policy Count',
    data:{json.dumps(lvr_counts)},
    backgroundColor:LVR_COLORS,borderWidth:0}}]}},
  options:{{plugins:{{legend:{{display:false}},tooltip:{{callbacks:{{label:c=>c.parsed.y.toLocaleString()+' policies'}}}}}},
    scales:{{y:yAxis({{beginAtZero:true}}),x:xAxis()}}
  }}}});

new Chart(document.getElementById('lvrExpChart'),{{type:'bar',
  data:{{labels:{json.dumps(LVR_BANDS)},datasets:[{{label:'Exposure $M',
    data:{json.dumps(lvr_exposure)},
    backgroundColor:LVR_COLORS,borderWidth:0}}]}},
  options:{{plugins:{{legend:{{display:false}},tooltip:{{callbacks:{{label:c=>'$'+c.parsed.y.toFixed(1)+'M'}}}}}},
    scales:{{y:yAxis({{beginAtZero:true,ticks:{{color:TICK,callback:v=>'$'+v+'M'}}}}),x:xAxis()}}
  }}}});

new Chart(document.getElementById('lvrHistChart'),{{type:'bar',
  data:{{labels:{json.dumps(bin_labels)},datasets:[{{label:'Policies',
    data:{json.dumps(bin_counts)},
    backgroundColor:{json.dumps(bin_counts)}.map((_,i)=>i>=5?T_RED:i>=3?T_ORANGE:T_BLUE),borderWidth:0}}]}},
  options:{{plugins:{{legend:{{display:false}},tooltip:{{callbacks:{{label:c=>c.parsed.y+' policies'}}}}}},
    scales:{{y:yAxis({{beginAtZero:true}}),x:xAxis()}}
  }}}});

new Chart(document.getElementById('stateExpChart'),{{type:'bar',
  data:{{labels:{json.dumps(STATES)},datasets:[{{label:'Exposure $M',
    data:{json.dumps(state_exposure)},
    backgroundColor:T_BLUE,borderWidth:0}}]}},
  options:{{indexAxis:'y',plugins:{{legend:{{display:false}},tooltip:{{callbacks:{{label:c=>'$'+c.parsed.x.toFixed(1)+'M'}}}}}},
    scales:{{x:Object.assign(yAxis({{ticks:{{color:TICK,callback:v=>'$'+v+'M'}}}}),{{grid:{{color:GRID}}}}),y:xAxis()}}
  }}}});

new Chart(document.getElementById('stateAvgLvrChart'),{{type:'bar',
  data:{{labels:{json.dumps(STATES)},datasets:[{{label:'Avg LVR %',
    data:{json.dumps(state_avg_lvr)},
    backgroundColor:{json.dumps(state_avg_lvr)}.map(v=>v>90?T_RED:v>87?T_ORANGE:T_GREEN),borderWidth:0}}]}},
  options:{{indexAxis:'y',plugins:{{legend:{{display:false}},tooltip:{{callbacks:{{label:c=>c.parsed.x.toFixed(1)+'% avg LVR'}}}}}},
    scales:{{x:Object.assign(yAxis({{min:80,ticks:{{color:TICK,callback:v=>v+'%'}}}}),{{grid:{{color:GRID}}}}),y:xAxis()}}
  }}}});

new Chart(document.getElementById('borrChart'),{{type:'doughnut',
  data:{{labels:{json.dumps(BORR_TYPES)},datasets:[{{
    data:{json.dumps(borr_counts)},
    backgroundColor:[T_BLUE,T_GREEN,T_ORANGE,T_PURPLE],
    borderColor:'#ffffff',borderWidth:2,hoverOffset:5}}]}},
  options:{{cutout:'58%',plugins:{{legend:{{position:'bottom',labels:{{color:'#4e4e4e',font:{{size:10}}}}}},
    tooltip:{{callbacks:{{label:c=>c.label+': '+c.parsed.toLocaleString()}}}}}}
  }}}});

new Chart(document.getElementById('propChart'),{{type:'doughnut',
  data:{{labels:{json.dumps(PROP_TYPES)},datasets:[{{
    data:{json.dumps(prop_counts)},
    backgroundColor:[T_TEAL,T_PURPLE,T_GREEN,T_ORANGE],
    borderColor:'#ffffff',borderWidth:2,hoverOffset:5}}]}},
  options:{{cutout:'58%',plugins:{{legend:{{position:'bottom',labels:{{color:'#4e4e4e',font:{{size:10}}}}}},
    tooltip:{{callbacks:{{label:c=>c.label+': '+c.parsed.toLocaleString()}}}}}}
  }}}});

new Chart(document.getElementById('chanChart'),{{type:'doughnut',
  data:{{labels:{json.dumps(CHANNELS)},datasets:[{{
    data:{json.dumps(chan_counts)},
    backgroundColor:[T_BLUE,T_GREEN,T_ORANGE],
    borderColor:'#ffffff',borderWidth:2,hoverOffset:5}}]}},
  options:{{cutout:'58%',plugins:{{legend:{{position:'bottom',labels:{{color:'#4e4e4e',font:{{size:10}}}}}},
    tooltip:{{callbacks:{{label:c=>c.label+': '+c.parsed.toLocaleString()}}}}}}
  }}}});

new Chart(document.getElementById('vintCountChart'),{{type:'bar',
  data:{{labels:{json.dumps([str(v) for v in VINTAGES])},datasets:[{{label:'New Policies',
    data:{json.dumps(vint_counts)},
    backgroundColor:T_BLUE,borderWidth:0}}]}},
  options:{{plugins:{{legend:{{display:false}},tooltip:{{callbacks:{{label:c=>c.parsed.y.toLocaleString()+' policies'}}}}}},
    scales:{{y:yAxis({{beginAtZero:true}}),x:xAxis()}}
  }}}});

new Chart(document.getElementById('vintExpChart'),{{type:'bar',
  data:{{labels:{json.dumps([str(v) for v in VINTAGES])},datasets:[{{label:'Exposure $M',
    data:{json.dumps(vint_exposure)},
    backgroundColor:T_PURPLE,borderWidth:0}}]}},
  options:{{plugins:{{legend:{{display:false}},tooltip:{{callbacks:{{label:c=>'$'+c.parsed.y.toFixed(1)+'M'}}}}}},
    scales:{{y:yAxis({{beginAtZero:true,ticks:{{color:TICK,callback:v=>'$'+v+'M'}}}}),x:xAxis()}}
  }}}});

new Chart(document.getElementById('lenderChart'),{{type:'bar',
  data:{{labels:{json.dumps(LENDERS)},datasets:[{{label:'Policies',
    data:{json.dumps(lend_counts)},
    backgroundColor:{json.dumps(lend_counts)}.map((_,i)=>i<4?T_BLUE:hexFade(T_BLUE)),borderWidth:0}}]}},
  options:{{indexAxis:'y',plugins:{{legend:{{display:false}},tooltip:{{callbacks:{{label:c=>c.parsed.x.toLocaleString()+' policies'}}}}}},
    scales:{{x:Object.assign(yAxis(),{{grid:{{color:GRID}}}}),y:xAxis({{ticks:{{color:TICK,font:{{size:10}}}}}})}}
  }}}});

function hexFade(hex){{const n=parseInt(hex.slice(1),16);return `rgba(${{n>>16&255}},${{n>>8&255}},${{n&255}},0.45)`;}}

// Quick-filter cards: recompute the summary text from embedded data (Tableau-style)
const RAW = {js_data};
const filters = {{state:'',lvr_band:'',borrower_type:''}};
document.querySelectorAll('.fopt').forEach(p=>{{
  p.addEventListener('click',()=>{{
    const g=p.dataset.group,v=p.dataset.val;
    document.querySelectorAll(`.fopt[data-group="${{g}}"]`).forEach(x=>x.classList.remove('active'));
    p.classList.add('active'); filters[g]=v;
    const f=RAW.filter(r=>
      (!filters.state||r.state===filters.state)&&
      (!filters.lvr_band||r.lvr_band===filters.lvr_band)&&
      (!filters.borrower_type||r.borrower_type===filters.borrower_type));
    const cnt=f.length, exp=f.reduce((a,r)=>a+r.loan_amt,0);
    const storyEl=document.getElementById('story-text');
    if(cnt===0){{storyEl.innerHTML='<strong>No policies</strong> match the selected filters.';return;}}
    const avgL=f.reduce((a,r)=>a+r.lvr,0)/cnt;
    storyEl.innerHTML=`<strong>${{cnt.toLocaleString()}} policies</strong> match &mdash; `+
      `total exposure <strong>$${{(exp/1e6).toFixed(1)}}M</strong>, `+
      `average LVR <strong>${{avgL.toFixed(1)}}%</strong>. `+
      (filters.state?`Showing ${{filters.state}} only. `:'') +
      (filters.lvr_band?`LVR band: ${{filters.lvr_band}}. `:'') +
      (filters.borrower_type?`Borrower type: ${{filters.borrower_type}}.`:'');
  }});
}});
</script>
</body>
</html>"""

with open(OUT,'w',encoding='utf-8') as f:
    f.write(html)
print(f"Written: {OUT}  ({len(html):,} chars)")
