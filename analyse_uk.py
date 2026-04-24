import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from matplotlib.patches import Patch

df = pd.read_csv("uk_ireland_shadow_fleet.csv")
df['last_position_UTC'] = pd.to_datetime(df['last_position_UTC'], errors='coerce')
df['SOG'] = pd.to_numeric(df['speed'], errors='coerce')
df['date'] = df['last_position_UTC'].dt.date

zone_counts = df.groupby('Zone')['mmsi'].count().sort_values(ascending=False)
chokepoints = zone_counts[zone_counts.index != 'UK_Other']
daily = df.groupby('date')['mmsi'].nunique()
daily.index = pd.to_datetime(daily.index)

fig, axes = plt.subplots(1, 3, figsize=(20, 8), facecolor='#0d1520')
fig.suptitle('Shadow fleet — UK & Irish Waters, Jan–Apr 2025\nSource: Datalastic API · Ukrainian GUR watchlist · 212 vessels · 47,477 pings', color='white', fontsize=13)

# Pie with explode and better labels
ax1 = axes[0]
ax1.set_facecolor('#0d1520')
colors = ['#185FA5','#3B6D11','#d44040','#e8a020','#8a4fd4','#3a9e9e']
explode = [0.03] * len(chokepoints)
wedges, texts, autotexts = ax1.pie(
    chokepoints.values,
    labels=None,
    colors=colors[:len(chokepoints)],
    autopct='%1.1f%%',
    startangle=90,
    explode=explode,
    pctdistance=0.75,
    textprops={'color':'white', 'fontsize':9},
    wedgeprops={'linewidth':2, 'edgecolor':'#0d1520'}
)
for at in autotexts:
    at.set_fontweight('bold')
    at.set_fontsize(9)
ax1.legend(
    wedges, chokepoints.index,
    loc='lower center',
    bbox_to_anchor=(0.5, -0.18),
    ncol=2,
    fontsize=8,
    facecolor='#0d1220',
    labelcolor='white',
    edgecolor='#2a3050'
)
ax1.set_title('Chokepoint distribution\n(excl. UK_Other)', color='white', fontsize=11)

# Top 15 vessels
ax2 = axes[1]
ax2.set_facecolor('#111827')
top15 = df.groupby('vessel_name')['mmsi'].count().sort_values(ascending=True).tail(15)
colors_bar = ['#d44040' if any(x in n for x in ['VORONIN','YEVGENOV','TOLL','GAKKEL','SAMOYLOVICH']) else '#185FA5' for n in top15.index]
ax2.barh(top15.index, top15.values, color=colors_bar, alpha=0.85)
ax2.set_title('Top 15 vessels by ping count', color='white', fontsize=11)
ax2.set_xlabel('AIS pings', color='#aaa')
ax2.tick_params(colors='#aaa', labelsize=8)
ax2.grid(True, color='#2a3050', linewidth=0.5, axis='x')
for spine in ax2.spines.values(): spine.set_color('#2a3050')
ax2.legend(handles=[
    Patch(color='#d44040', label='Russian Arctic fleet'),
    Patch(color='#185FA5', label='Shadow fleet tanker')
], facecolor='#0d1220', labelcolor='white', edgecolor='#2a3050', fontsize=8)

# Daily chart
ax3 = axes[2]
ax3.set_facecolor('#111827')
daily_roll = daily.rolling(7, min_periods=1).mean()
ax3.bar(daily.index, daily.values, color='#185FA5', alpha=0.3, width=1)
ax3.plot(daily.index, daily_roll, color='#185FA5', linewidth=2, label='7-day avg')
ax3.axhline(daily.mean(), color='#00d4ff', linewidth=1, linestyle=':', label=f'Mean: {daily.mean():.1f}/day')
ax3.set_title('Daily unique vessels in UK/Irish waters', color='white', fontsize=11)
ax3.set_ylabel('Unique vessels', color='#aaa')
ax3.tick_params(colors='#aaa', labelsize=8)
ax3.legend(facecolor='#0d1220', labelcolor='white', edgecolor='#2a3050', fontsize=8)
ax3.grid(True, color='#2a3050', linewidth=0.5)
for spine in ax3.spines.values(): spine.set_color('#2a3050')
ax3.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45, ha='right', color='#aaa')

plt.tight_layout()
plt.savefig('uk_ireland_analysis.png', dpi=150, bbox_inches='tight', facecolor='#0d1520')
print("Saved uk_ireland_analysis.png")