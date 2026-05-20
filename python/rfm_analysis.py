"""
E-Commerce RFM Customer Segmentation
Week 2: RFM Scoring & Customer Segmentation
Author: G. Jeshwanth
Dataset: UCI Online Retail II
"""

import pandas as pd
from sqlalchemy import create_engine

# ── 1. Connect to MySQL and load clean data ──────────────────────────────
print("Connecting to MySQL...")
engine = create_engine('mysql+mysqlconnector://root:root@localhost/retail_rfm')

df = pd.read_sql("SELECT * FROM online_retail_clean", engine)
print(f"✅ Loaded {len(df)} rows")
print(df.head())

# ── 2. Parse dates ───────────────────────────────────────────────────────
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])

# Reference date = 1 day after the last transaction
reference_date = df['InvoiceDate'].max() + pd.Timedelta(days=1)
print(f"\nReference date: {reference_date.date()}")

# ── 3. Calculate R, F, M per customer ───────────────────────────────────
rfm = df.groupby('CustomerID').agg(
    last_purchase = ('InvoiceDate', 'max'),
    frequency     = ('Invoice',     'nunique'),
    monetary      = ('Revenue',     'sum')
).reset_index()

rfm['recency'] = (reference_date - rfm['last_purchase']).dt.days
rfm.drop(columns='last_purchase', inplace=True)

print("\nRFM table sample:")
print(rfm.head(10))
print(f"\nTotal unique customers: {len(rfm)}")

# ── 4. Score 1-5 using quartiles ─────────────────────────────────────────
# Recency: lower days = better = score 5
rfm['R'] = pd.qcut(rfm['recency'],  q=5, labels=[5,4,3,2,1])

# Frequency and Monetary: higher = better = score 5
rfm['F'] = pd.qcut(rfm['frequency'].rank(method='first'), q=5, labels=[1,2,3,4,5])
rfm['M'] = pd.qcut(rfm['monetary'].rank(method='first'),  q=5, labels=[1,2,3,4,5])

# Convert to int
rfm[['R','F','M']] = rfm[['R','F','M']].astype(int)

# Combined RFM score string e.g. "555"
rfm['RFM_Score'] = rfm['R'].astype(str) + rfm['F'].astype(str) + rfm['M'].astype(str)

print("\nScore distribution:")
print(rfm[['R','F','M']].describe().round(1))

# ── 5. Assign segments ────────────────────────────────────────────────────
def segment(row):
    r, f, m = row['R'], row['F'], row['M']
    if r >= 4 and f >= 4 and m >= 4:
        return 'Champion'
    elif f >= 3 and m >= 3:
        return 'Loyal Customer'
    elif r >= 4 and f == 1:
        return 'New Customer'
    elif r >= 3 and f == 2:
        return 'Promising'
    elif r <= 2 and f >= 3:
        return 'At Risk'
    elif r == 1 and f == 1 and m == 1:
        return 'Lost'
    else:
        return 'Needs Attention'

rfm['Segment'] = rfm.apply(segment, axis=1)

# ── 6. Segment summary ────────────────────────────────────────────────────
summary = rfm.groupby('Segment').agg(
    customers     = ('CustomerID', 'count'),
    avg_recency   = ('recency',    'mean'),
    avg_frequency = ('frequency',  'mean'),
    avg_monetary  = ('monetary',   'mean'),
    total_revenue = ('monetary',   'sum')
).round(2).sort_values('total_revenue', ascending=False)

print("\n📊 SEGMENT SUMMARY:")
print(summary.to_string())

# ── 7. Export to CSV ──────────────────────────────────────────────────────
rfm.to_csv('data/rfm_output.csv', index=False)
summary.to_csv('data/rfm_summary.csv')
print("\n✅ Files saved:")
print("   data/rfm_output.csv   — one row per customer with scores & segment")
print("   data/rfm_summary.csv  — segment-level summary for dashboard")
