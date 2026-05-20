"""
E-Commerce RFM Customer Segmentation
Week 3: Data Visualizations (6 Charts)
Author: G. Jeshwanth
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from sqlalchemy import create_engine

# ── Setup ────────────────────────────────────────────────────────────────
engine = create_engine('mysql+mysqlconnector://root:root@localhost/retail_rfm')
save_path = 'charts/'

COLORS = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#3B1F2B', '#44BBA4', '#E94F37']
sns.set_theme(style='whitegrid', font_scale=1.1)

# Load RFM output
rfm = pd.read_csv('data/rfm_output.csv')
print(f"✅ RFM data loaded: {len(rfm)} customers")

# ── Chart 1: Customer count by segment ───────────────────────────────────
seg_count = rfm['Segment'].value_counts().reset_index()
seg_count.columns = ['Segment', 'Customers']

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(seg_count['Segment'], seg_count['Customers'],
              color=COLORS, edgecolor='white', linewidth=0.8)
ax.bar_label(bars, fmt='%d', padding=4, fontsize=10)
ax.set_title('Customer Count by Segment', fontsize=15, fontweight='bold', pad=15)
ax.set_xlabel('Segment', fontsize=12)
ax.set_ylabel('Number of Customers', fontsize=12)
ax.tick_params(axis='x', rotation=20)
plt.tight_layout()
plt.savefig(save_path + 'chart1_segment_count.png', dpi=150)
plt.close()
print("✅ Chart 1 saved")

# ── Chart 2: Revenue by segment ───────────────────────────────────────────
seg_rev = rfm.groupby('Segment')['monetary'].sum().sort_values(ascending=True)

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(seg_rev.index, seg_rev.values, color=COLORS[:len(seg_rev)],
               edgecolor='white')
ax.bar_label(bars, fmt='£{:,.0f}', padding=4, fontsize=9)
ax.set_title('Total Revenue by Segment', fontsize=15, fontweight='bold', pad=15)
ax.set_xlabel('Total Revenue (£)', fontsize=12)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'£{x/1e6:.1f}M'))
plt.tight_layout()
plt.savefig(save_path + 'chart2_revenue_by_segment.png', dpi=150)
plt.close()
print("✅ Chart 2 saved")

# ── Chart 3: Monthly revenue trend ────────────────────────────────────────
df = pd.read_sql("SELECT InvoiceDate, Revenue FROM online_retail_clean", engine)
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
df['Month'] = df['InvoiceDate'].dt.to_period('M')
monthly = df.groupby('Month')['Revenue'].sum().reset_index()
monthly['Month'] = monthly['Month'].astype(str)

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(monthly['Month'], monthly['Revenue'], color='#2E86AB',
        linewidth=2.5, marker='o', markersize=5)
ax.fill_between(range(len(monthly)), monthly['Revenue'],
                alpha=0.15, color='#2E86AB')
ax.set_title('Monthly Revenue Trend (2009-2011)', fontsize=15, fontweight='bold', pad=15)
ax.set_xlabel('Month', fontsize=12)
ax.set_ylabel('Revenue (£)', fontsize=12)
ax.set_xticks(range(len(monthly)))
ax.set_xticklabels(monthly['Month'], rotation=45, ha='right', fontsize=8)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'£{x/1e6:.1f}M'))
plt.tight_layout()
plt.savefig(save_path + 'chart3_monthly_trend.png', dpi=150)
plt.close()
print("✅ Chart 3 saved")

# ── Chart 4: RFM heatmap ──────────────────────────────────────────────────
heatmap_data = rfm.groupby(['R', 'F'])['monetary'].mean().unstack()

fig, ax = plt.subplots(figsize=(9, 7))
sns.heatmap(heatmap_data, annot=True, fmt='.0f', cmap='YlOrRd',
            linewidths=0.5, ax=ax,
            cbar_kws={'label': 'Avg Monetary Value (£)'})
ax.set_title('Avg Spend: Recency vs Frequency Score', fontsize=15,
             fontweight='bold', pad=15)
ax.set_xlabel('Frequency Score', fontsize=12)
ax.set_ylabel('Recency Score', fontsize=12)
plt.tight_layout()
plt.savefig(save_path + 'chart4_rfm_heatmap.png', dpi=150)
plt.close()
print("✅ Chart 4 saved")

# ── Chart 5: Recency distribution ────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 6))
ax.hist(rfm['recency'], bins=40, color='#2E86AB', edgecolor='white',
        linewidth=0.6, alpha=0.85)
ax.axvline(rfm['recency'].median(), color='#C73E1D', linewidth=2,
           linestyle='--', label=f"Median: {rfm['recency'].median():.0f} days")
ax.set_title('Customer Recency Distribution', fontsize=15, fontweight='bold', pad=15)
ax.set_xlabel('Days Since Last Purchase', fontsize=12)
ax.set_ylabel('Number of Customers', fontsize=12)
ax.legend(fontsize=11)
plt.tight_layout()
plt.savefig(save_path + 'chart5_recency_dist.png', dpi=150)
plt.close()
print("✅ Chart 5 saved")

# ── Chart 6: Top 10 products ──────────────────────────────────────────────
top_products = pd.read_sql("""
    SELECT Description,
           ROUND(SUM(Revenue), 2) AS revenue
    FROM online_retail_clean
    GROUP BY Description
    ORDER BY revenue DESC
    LIMIT 10
""", engine)

fig, ax = plt.subplots(figsize=(11, 6))
bars = ax.barh(top_products['Description'][::-1],
               top_products['revenue'][::-1],
               color='#44BBA4', edgecolor='white')
ax.bar_label(bars, fmt='£{:,.0f}', padding=4, fontsize=9)
ax.set_title('Top 10 Products by Revenue', fontsize=15, fontweight='bold', pad=15)
ax.set_xlabel('Revenue (£)', fontsize=12)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'£{x/1e3:.0f}K'))
plt.tight_layout()
plt.savefig(save_path + 'chart6_top_products.png', dpi=150)
plt.close()
print("✅ Chart 6 saved")

print("\n🎉 All 6 charts saved to charts/ folder!")
