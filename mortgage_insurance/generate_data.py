"""
Mortgage Insurance — synthetic data generator
Produces three CSV files for Tableau:
  data/loans.csv          — one row per insured loan
  data/arrears_monthly.csv — monthly arrears snapshots (Jan 2022 – Dec 2024)
  data/claims.csv         — one row per lodged claim
"""

import pandas as pd
import numpy as np
import random
import os
from datetime import datetime, timedelta

np.random.seed(42)
random.seed(42)

OUT = r"C:\Users\madel\tableau\mortgage_insurance\data"
os.makedirs(OUT, exist_ok=True)

# ── Config ────────────────────────────────────────────────────────────────────
N_LOANS = 2000
LOAN_START  = datetime(2019, 1, 1)
LOAN_END    = datetime(2024, 6, 30)
SNAP_START  = datetime(2022, 1, 1)
SNAP_END    = datetime(2024, 12, 31)

STATES        = ['NSW','VIC','QLD','WA','SA','TAS','ACT','NT']
STATE_W       = [0.34, 0.27, 0.18, 0.10, 0.06, 0.015, 0.02, 0.005]
STATE_PROPVAL = {          # (min, max) property value AUD
    'NSW': (720000,1800000), 'VIC': (580000,1300000),
    'QLD': (420000, 950000), 'WA':  (380000, 850000),
    'SA':  (350000, 720000), 'TAS': (300000, 620000),
    'ACT': (620000,1150000), 'NT':  (320000, 600000),
}
STATE_POSTCODES = {
    'NSW': ['2000','2010','2020','2060','2090','2100','2150','2170','2200','2750','2300','2500'],
    'VIC': ['3000','3004','3008','3011','3055','3070','3121','3145','3168','3175','3220','3350'],
    'QLD': ['4000','4005','4010','4051','4069','4101','4122','4179','4207','4217','4350','4700'],
    'WA':  ['6000','6003','6005','6010','6018','6027','6050','6065','6100','6150','6160','6210'],
    'SA':  ['5000','5006','5008','5011','5034','5046','5063','5095','5107','5108','5290','5600'],
    'TAS': ['7000','7005','7009','7011','7018','7050','7054','7248','7250','7310'],
    'ACT': ['2600','2601','2602','2603','2605','2607','2609','2611','2614','2617'],
    'NT':  ['0800','0810','0820','0830','0850','0870','0880'],
}
STATE_SUBURBS = {
    'NSW': ['Sydney CBD','Parramatta','Blacktown','Liverpool','Penrith','Campbelltown',
            'Newcastle','Wollongong','Gosford','Maitland','Chatswood','Bondi'],
    'VIC': ['Melbourne CBD','Dandenong','Frankston','Geelong','Ballarat','Bendigo',
            'Ringwood','Box Hill','Werribee','Craigieburn','Footscray','St Kilda'],
    'QLD': ['Brisbane CBD','Gold Coast','Sunshine Coast','Townsville','Cairns',
            'Logan','Ipswich','Toowoomba','Mackay','Rockhampton','Maroochydore','Redcliffe'],
    'WA':  ['Perth CBD','Fremantle','Mandurah','Joondalup','Rockingham','Armadale',
            'Bunbury','Geraldton','Kalgoorlie','Albany','Baldivis','Cannington'],
    'SA':  ['Adelaide CBD','Mount Gambier','Whyalla','Murray Bridge','Port Augusta',
            'Victor Harbor','Gawler','Elizabeth','Salisbury','Marion','Morphett Vale','Tea Tree Gully'],
    'TAS': ['Hobart','Launceston','Devonport','Burnie','Kingston',
            'Glenorchy','Clarence','Sorell','New Norfolk','Ulverstone'],
    'ACT': ['Canberra City','Belconnen','Tuggeranong','Gungahlin',
            'Woden','Weston Creek','Molonglo','Casey','Bonner','Forde'],
    'NT':  ['Darwin CBD','Palmerston','Alice Springs','Katherine',
            'Nhulunbuy','Tennant Creek','Casuarina','Rapid Creek'],
}

LVR_BANDS   = ['≤80%','80-85%','85-90%','90-95%','95%+']
LVR_BAND_W  = [0.05, 0.20, 0.35, 0.30, 0.10]
LVR_RANGES  = {'≤80%':(65,80),'80-85%':(80.1,85),'85-90%':(85.1,90),'90-95%':(90.1,95),'95%+':(95.1,98)}
DEFAULT_RATE = {'≤80%':0.005,'80-85%':0.013,'85-90%':0.022,'90-95%':0.038,'95%+':0.058}
PREMIUM_PCT  = {'≤80%':0.005,'80-85%':0.009,'85-90%':0.014,'90-95%':0.021,'95%+':0.030}

LENDERS   = ['Commonwealth Bank','Westpac','ANZ','NAB','Macquarie',
             'Bendigo Bank','Bank of Queensland','ING','Suncorp','AMP Bank']
LENDER_W  = [0.25,0.20,0.17,0.15,0.08,0.05,0.04,0.03,0.02,0.01]
CHANNELS  = ['Bank Branch','Mortgage Broker','Online / Direct']
CHANNEL_W = [0.33,0.50,0.17]
PROP_TYPES = ['House','Apartment','Townhouse','Land']
PROP_W     = [0.60,0.28,0.10,0.02]
BORR_TYPES = ['First Home Buyer','Owner Occupier','Investor','Refinancer']
BORR_W     = [0.38,0.35,0.22,0.05]
EMP_TYPES  = ['PAYG','Self-Employed','Contract']
EMP_W      = [0.70,0.20,0.10]

def rdate(start, end):
    return start + timedelta(days=random.randint(0,(end-start).days))

def lvr_from_band(band):
    lo, hi = LVR_RANGES[band]
    return round(random.uniform(lo, hi), 2)

# ── 1. LOANS ──────────────────────────────────────────────────────────────────
print("Generating loans.csv ...")
rows = []
for i in range(N_LOANS):
    state     = random.choices(STATES, STATE_W)[0]
    lvr_band  = random.choices(LVR_BANDS, LVR_BAND_W)[0]
    lvr       = lvr_from_band(lvr_band)
    orig_date = rdate(LOAN_START, LOAN_END)
    sett_date = orig_date + timedelta(days=random.randint(14,45))

    pv_lo, pv_hi = STATE_PROPVAL[state]
    prop_val  = round(random.uniform(pv_lo, pv_hi) / 1000) * 1000
    loan_amt  = round(prop_val * lvr / 100 / 100) * 100
    premium   = round(loan_amt * PREMIUM_PCT[lvr_band] / 50) * 50

    dr = DEFAULT_RATE[lvr_band]
    r  = random.random()
    if r < dr:
        status = random.choices(['Default','Claim Paid'],[0.4,0.6])[0]
    elif r < dr * 4:
        status = 'In Arrears'
    elif sett_date < datetime(2022,1,1):
        status = random.choices(['Active','Closed'],[0.55,0.45])[0]
    else:
        status = 'Active'

    postcode = random.choice(STATE_POSTCODES[state])
    suburb   = random.choice(STATE_SUBURBS[state])

    rows.append(dict(
        loan_id            = f"LMI{10000+i}",
        certificate_number = f"CERT-{orig_date.year}-{str(i).zfill(5)}",
        origination_date   = orig_date.strftime('%Y-%m-%d'),
        settlement_date    = sett_date.strftime('%Y-%m-%d'),
        vintage_year       = orig_date.year,
        lender             = random.choices(LENDERS, LENDER_W)[0],
        lender_channel     = random.choices(CHANNELS, CHANNEL_W)[0],
        state              = state,
        suburb             = suburb,
        postcode           = postcode,
        property_type      = random.choices(PROP_TYPES, PROP_W)[0],
        borrower_type      = random.choices(BORR_TYPES, BORR_W)[0],
        employment_type    = random.choices(EMP_TYPES, EMP_W)[0],
        lvr                = lvr,
        lvr_band           = lvr_band,
        property_value     = prop_val,
        loan_amount        = loan_amt,
        insured_amount     = loan_amt,
        premium_amount     = premium,
        loan_status        = status,
    ))

df_loans = pd.DataFrame(rows)
df_loans.to_csv(f"{OUT}/loans.csv", index=False)
print(f"  {len(df_loans):,} rows  →  loans.csv")
print(df_loans['lvr_band'].value_counts().to_string())
print(df_loans['state'].value_counts().to_string())

# ── 2. MONTHLY ARREARS SNAPSHOTS ──────────────────────────────────────────────
print("\nGenerating arrears_monthly.csv ...")

# Pre-index loans for fast lookup
loan_lookup = df_loans.set_index('loan_id').to_dict('index')
eligible_ids = df_loans[
    df_loans['loan_status'].isin(['Active','In Arrears','Default','Claim Paid'])
]['loan_id'].tolist()

# State adjustment multipliers (higher = more arrears)
STATE_MULT = {'NSW':1.12,'VIC':1.06,'QLD':0.94,'WA':0.88,'SA':0.83,'TAS':0.78,'ACT':0.72,'NT':1.20}
LVR_MULT   = {'≤80%':0.40,'80-85%':0.80,'85-90%':1.00,'90-95%':1.55,'95%+':2.30}

# Base 30-day arrears rate by month (reflecting RBA rate hike cycle)
def base_rate(dt):
    if dt < datetime(2022, 5, 1):   return 0.018   # pre-hikes
    if dt < datetime(2023, 1, 1):   return 0.030   # rapid hikes
    if dt < datetime(2023, 7, 1):   return 0.042   # peak stress
    if dt < datetime(2024, 1, 1):   return 0.036   # stabilising
    return 0.028                                    # 2024 easing

snap_rows = []
dt = SNAP_START
while dt <= SNAP_END:
    br = base_rate(dt)
    for lid in eligible_ids:
        loan = loan_lookup[lid]
        sett = datetime.strptime(loan['settlement_date'], '%Y-%m-%d')
        if sett >= dt:
            continue   # loan not yet settled
        adj = br * LVR_MULT.get(loan['lvr_band'],1.0) * STATE_MULT.get(loan['state'],1.0)
        r = random.random()
        if r < adj * 0.04:
            bucket, days = '90+', random.randint(91,180)
        elif r < adj * 0.12:
            bucket, days = '90',  random.randint(76,90)
        elif r < adj * 0.30:
            bucket, days = '60',  random.randint(46,75)
        elif r < adj:
            bucket, days = '30',  random.randint(15,45)
        else:
            continue   # current — not in arrears

        snap_rows.append(dict(
            snapshot_date   = dt.strftime('%Y-%m-%d'),
            snapshot_month  = dt.strftime('%b %Y'),
            loan_id         = lid,
            state           = loan['state'],
            lvr_band        = loan['lvr_band'],
            borrower_type   = loan['borrower_type'],
            property_type   = loan['property_type'],
            employment_type = loan['employment_type'],
            lender          = loan['lender'],
            arrears_bucket  = bucket,
            days_in_arrears = days,
            arrears_amount  = round(loan['loan_amount'] * random.uniform(0.002,0.009), 2),
            loan_amount     = loan['loan_amount'],
        ))
    # Advance one month
    dt = datetime(dt.year + (dt.month == 12), (dt.month % 12) + 1, 1)

df_arrears = pd.DataFrame(snap_rows)
df_arrears.to_csv(f"{OUT}/arrears_monthly.csv", index=False)
print(f"  {len(df_arrears):,} rows  →  arrears_monthly.csv")

# ── 3. CLAIMS ─────────────────────────────────────────────────────────────────
print("\nGenerating claims.csv ...")
RECOVERY_PCT = {'≤80%':0.88,'80-85%':0.78,'85-90%':0.68,'90-95%':0.58,'95%+':0.46}

claim_rows = []
for _, loan in df_loans[df_loans['loan_status'].isin(['Default','Claim Paid'])].iterrows():
    sett = datetime.strptime(loan['settlement_date'], '%Y-%m-%d')
    claim_date = sett + timedelta(days=random.randint(180,1400))
    if claim_date > datetime(2024,12,31):
        claim_date = datetime(2024,12,31)

    claim_amt    = round(loan['loan_amount'] * random.uniform(0.04, 0.20), 2)
    rec_rate     = RECOVERY_PCT.get(loan['lvr_band'], 0.65) * random.uniform(0.85,1.15)
    recovery_amt = round(claim_amt * rec_rate, 2)
    net_loss     = round(max(0, claim_amt - recovery_amt), 2)

    claim_rows.append(dict(
        claim_id        = f"CLM{50000+len(claim_rows)}",
        loan_id         = loan['loan_id'],
        claim_date      = claim_date.strftime('%Y-%m-%d'),
        claim_year      = claim_date.year,
        state           = loan['state'],
        lvr_band        = loan['lvr_band'],
        lender          = loan['lender'],
        borrower_type   = loan['borrower_type'],
        employment_type = loan['employment_type'],
        property_type   = loan['property_type'],
        claim_amount    = claim_amt,
        recovery_amount = recovery_amt,
        net_loss        = net_loss,
        loss_ratio      = round(net_loss / loan['premium_amount'], 4) if loan['premium_amount'] else None,
        claim_status    = 'Paid' if loan['loan_status'] == 'Claim Paid' else 'Open',
    ))

df_claims = pd.DataFrame(claim_rows)
df_claims.to_csv(f"{OUT}/claims.csv", index=False)
print(f"  {len(df_claims):,} rows  →  claims.csv")

# ── Summary ───────────────────────────────────────────────────────────────────
print("\n── Summary ──────────────────────────────────────────")
print(f"loans.csv          {len(df_loans):>6,} rows")
print(f"arrears_monthly.csv{len(df_arrears):>6,} rows")
print(f"claims.csv         {len(df_claims):>6,} rows")
print(f"\nFiles saved to: {OUT}")
