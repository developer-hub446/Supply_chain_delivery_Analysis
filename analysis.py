# Run from this project directory. Notebook companion with identical code.

from pathlib import Path
import json, sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display
BASE = Path.cwd()
assert (BASE/'data/raw.csv').exists(), 'Run from this project directory'
OUT = BASE/'outputs'
OUT.mkdir(exist_ok=True)
pd.set_option('display.max_columns', 20)
plt.rcParams.update({'figure.dpi':120, 'axes.spines.top':False, 'axes.spines.right':False})
df = pd.read_csv(BASE/'data/raw.csv')
if 'date' in df:
    df['date'] = pd.to_datetime(df['date'])
print('Raw shape:',df.shape)
display(df.head())


audit=pd.DataFrame({'dtype':df.dtypes.astype(str),'missing':df.isna().sum(),'unique_values':df.nunique()})
display(audit)
print('Exact duplicate rows:',df.duplicated().sum())
audit.to_csv(OUT/'data_quality.csv')


assert df.po_id.is_unique and (df.delivered_units<=df.ordered_units).all()
df['otif']=((df.actual_days<=df.promised_days)&(df.delivered_units==df.ordered_units)).astype(int)
df['coverage_days']=df.stock_units/df.daily_demand
summary=df.groupby('supplier').agg(orders=('po_id','size'),otif_rate=('otif','mean'),ordered=('ordered_units','sum'),delivered=('delivered_units','sum'))
summary['fill_rate_pct']=100*summary.delivered/summary.ordered
metrics={'OTIF (%)':100*df.otif.mean(),'Unit fill rate (%)':100*df.delivered_units.sum()/df.ordered_units.sum(),'Snapshots below 7 days coverage':int((df.coverage_days<7).sum())}
chart=summary.otif_rate*100; ylabel='On-time-in-full orders (%)'


df['late_days']=(df.actual_days-df.promised_days).clip(lower=0)
detail=df.groupby('supplier').agg(mean_late_days=('late_days','mean'),p90_late_days=('late_days',lambda x:x.quantile(.9)),median_coverage_days=('coverage_days','median'))
display(detail.round(3))
fig,ax=plt.subplots(figsize=(8,4));detail.mean_late_days.plot.bar(ax=ax,color='#a06536',rot=0);ax.set_ylabel('Mean positive delay (days)');ax.set_title('Delivery delay severity');fig.tight_layout();fig.savefig(OUT/'detail.png');plt.show()
worst=summary.otif_rate.idxmin()
recommendation=f'{worst} has the lowest OTIF rate ({summary.loc[worst,"otif_rate"]:.2%}). Review order size, lead time and delay causes before changing suppliers.'

# Exploratory analysis: distributions, failure modes, monthly trend and coverage by supplier
display(df[['ordered_units','delivered_units','promised_days','actual_days','stock_units','daily_demand','coverage_days']].describe().round(2).T)
late = df.actual_days > df.promised_days
short = df.delivered_units < df.ordered_units
failure_mode = pd.Series(np.select([late & short, late, short], ['late and short', 'late only', 'short only'], 'on time and full'), index=df.index)
display((pd.crosstab(df.supplier, failure_mode, normalize='index') * 100).round(1))
monthly = df.groupby(df.date.dt.to_period('M')).agg(orders=('po_id','size'), otif_pct=('otif','mean'))
monthly['otif_pct'] *= 100
display(monthly.round(2).T)
low = df.assign(low_cov=df.coverage_days < 7).groupby('supplier').agg(low_coverage_snapshots=('low_cov','sum'), low_coverage_share_pct=('low_cov','mean'))
low['low_coverage_share_pct'] *= 100
display(low.round(2))
fig, axes = plt.subplots(1, 2, figsize=(11, 3.8))
df.coverage_days.clip(upper=60).plot.hist(bins=30, ax=axes[0], color='#246577')
axes[0].axvline(7, color='#a06536', ls='--'); axes[0].set_title('Coverage days (capped at 60; dashed = 7 days)')
monthly.otif_pct.plot(ax=axes[1], marker='o', color='#246577'); axes[1].set_title('Monthly OTIF (%)'); axes[1].set_xlabel('')
fig.tight_layout(); plt.show()

detail.to_csv(OUT/'detail.csv')
print(recommendation)
(OUT/'recommendation.txt').write_text(recommendation+'\n')


display(summary.round(4))
display(pd.Series(metrics,name='value').to_frame())
summary.to_csv(OUT/'summary.csv')
(OUT/'metrics.json').write_text(json.dumps({k:float(v) for k,v in metrics.items()},indent=2))
df.to_csv(OUT/'analysis_ready.csv',index=False)
assert all(np.isfinite(float(v)) for v in metrics.values()), 'Invalid KPI'


import re
queries = {m.group(1): m.group(2).strip() for m in re.finditer(r'-- name: (\w+)\n(.*?;)', (BASE/'analysis.sql').read_text(), re.S)}
with sqlite3.connect(':memory:') as conn:
    df.to_sql('facts', conn, index=False, if_exists='replace')
    sql_tables = {name: pd.read_sql_query(q, conn) for name, q in queries.items()}
for name, table in sql_tables.items():
    print('SQL query:', name)
    display(table)
sql_result = sql_tables['supplier_kpis']
sql_result.to_csv(OUT/'sql_results.csv', index=False)
# Reconcile every supplier-level measure against the independent pandas calculations.
sql_check = sql_result.set_index('supplier').sort_index()
expected = pd.DataFrame({'orders': summary.orders, 'otif_pct': 100*summary.otif_rate, 'fill_rate_pct': summary.fill_rate_pct,
                         'low_coverage_snapshots': low.low_coverage_snapshots, 'mean_late_days': detail.mean_late_days}).sort_index()
assert list(sql_check.index) == list(expected.index) and list(sql_check.columns) == list(expected.columns)
assert np.allclose(sql_check.to_numpy(float), expected.to_numpy(float), rtol=1e-8, atol=1e-6)
assert int(sql_check.low_coverage_snapshots.sum()) == metrics['Snapshots below 7 days coverage']
assert sql_tables['monthly_otif'].orders.sum() == len(df) and sql_tables['failure_modes'].late_orders.sum() == int(late.sum())
print('SQL / Python reconciliation passed:', list(expected.columns))


fig,ax=plt.subplots(figsize=(9,4.6))
chart.plot(kind='bar',ax=ax,color='#246577',rot=25)
ax.set_ylabel(ylabel)
ax.set_xlabel('')
ax.set_title('Supply Chain Delivery and Inventory Risk',loc='left',fontweight='bold',pad=15)
fig.tight_layout()
fig.savefig(OUT/'overview.png',bbox_inches='tight')
plt.show()


# Standalone dashboard: no remote JavaScript, server or account required.
import html, base64
cards=''.join('<article><span>'+html.escape(k)+'</span><strong>'+f'{v:,.4f}'+'</strong></article>' for k,v in metrics.items())
image=base64.b64encode((OUT/'overview.png').read_bytes()).decode()
table=summary.round(4).to_html(classes='data',border=0)
page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Supply Chain Delivery and Inventory Risk</title>
<style>body{font:16px system-ui;margin:0;background:#f3f5f7;color:#172c3b}main{max-width:1100px;margin:auto;padding:36px}header{border-bottom:3px solid #246577;margin-bottom:24px}small{color:#51616c}.cards{display:flex;gap:14px;flex-wrap:wrap}article{background:white;padding:18px;border:1px solid #d7e0e5;flex:1;min-width:175px}strong{display:block;font-size:27px;margin-top:12px}img{max-width:100%;margin-top:24px}table{border-collapse:collapse;background:white;width:100%;font-size:14px}td,th{padding:12px;text-align:right;border-bottom:1px solid #d7e0e5}input{padding:12px;margin:20px 0;width:280px;max-width:90%}.scroll{overflow:auto}footer{margin-top:24px}</style>
<main><header><small>Rohan Kumar · DATA ANALYST PORTFOLIO</small><h1>Supply Chain Delivery and Inventory Risk</h1><p>Which suppliers miss delivery commitments?</p><p><b>Synthetic teaching data · Fictional 2025 case study</b></p></header><section class="cards">'''+cards+'''</section><img alt="Analysis overview chart" src="data:image/png;base64,'''+image+'''"><h2>Explore summary groups</h2><label for="filter">Filter summary rows</label><br><input id="filter" placeholder="Type a group name"><div class="scroll">'''+table+'''</div><p>Coverage is a snapshot heuristic using average daily demand. It omits variability, replenishment timing and service-level safety stock.</p><footer><a href="https://www.linkedin.com/in/rohankumarray/">LinkedIn</a> · <a href="https://github.com/developer-hub446">GitHub</a> · <a href="mailto:rk7038303@gmail.com">Email</a></footer></main>
<script>document.getElementById('filter').addEventListener('input',function(){const q=this.value.toLowerCase();document.querySelectorAll('tbody tr').forEach(r=>r.hidden=!r.textContent.toLowerCase().includes(q))});</script></html>'''
detail_image=base64.b64encode((OUT/'detail.png').read_bytes()).decode()
page=page.replace('<h2>Explore summary groups</h2>','<h2>Analyst finding</h2><p>'+html.escape(recommendation)+'</p><img alt="Supporting analysis" src="data:image/png;base64,'+detail_image+'"><h2>Explore summary groups</h2>')
(OUT/'dashboard.html').write_text(page)
print('Saved dashboard.html, overview.png, summary.csv, metrics.json, SQL results and analysis-ready data.')
