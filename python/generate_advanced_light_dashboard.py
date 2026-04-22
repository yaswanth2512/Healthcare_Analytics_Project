import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import Rectangle, FancyBboxPatch
from datetime import datetime
import numpy as np
import os
import matplotlib.dates as mdates

out_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tableau', 'Enterprise_Tableau_Dark_Mode.png'))
data_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'claims.csv'))

# Load standard data
try:
    df_claims = pd.read_csv(data_file)
    df_claims['service_date'] = pd.to_datetime(df_claims['service_date'])
    df_claims['month'] = df_claims['service_date'].dt.to_period('M')
except Exception as e:
    df_claims = pd.DataFrame()

# Math validation for exact Tableau KPI logic
total_claims = f"{len(df_claims):,}"
total_paid = f"${df_claims['approved_amount'].sum()/1_000_000:.1f}M"
rejection_pct = f"{(len(df_claims[df_claims['claim_status'] == 'Denied']) / max(1, len(df_claims))) * 100:.1f}%"

# Tableau Standard Light Theme Constants
bg_color = '#F3F5F8'
panel_color = '#FFFFFF'
text_color = '#333333'
subtext_color = '#666666'
grid_color = '#E9ECEF'
tableau_blue = '#4E79A7'
tableau_green = '#59A14F'
tableau_red = '#E15759'
tableau_orange = '#F28E2B'

fig = plt.figure(figsize=(18, 10.5), facecolor=bg_color)
plt.rcParams['font.sans-serif'] = ['Segoe UI', 'Arial', 'sans-serif']

# ---- MOCK TABLEAU UI (Top Menu) ----
rect = Rectangle((0, 0.95), 1, 0.05, transform=fig.transFigure, facecolor='#2C3E50', zorder=1)
fig.patches.append(rect)
fig.text(0.01, 0.965, 'File   Data   Worksheet   Dashboard   Story   Analysis   Map   Format   Server   Window   Help', fontsize=11, color='#BDC3C7', zorder=2)

# ---- DASHBOARD TITLE BAND ----
rect_title = Rectangle((0.02, 0.88), 0.78, 0.06, transform=fig.transFigure, facecolor=panel_color, edgecolor='#D1D5D8', zorder=1)
fig.patches.append(rect_title)
today_str = datetime.now().strftime('%B %d, %Y')
fig.text(0.03, 0.90, f'Healthcare Analytics: Executive Overview', fontsize=22, fontweight='bold', color=text_color, zorder=2)
fig.text(0.60, 0.895, f'Update: {today_str} | Data: Snowflake', fontsize=11, color=subtext_color, zorder=2, fontstyle='italic')

# ---- FILTERS SIDEBAR (Authentic Tableau Look) ----
rect_sidebar = Rectangle((0.81, 0.05), 0.17, 0.89, transform=fig.transFigure, facecolor=panel_color, edgecolor='#D1D5D8', zorder=1)
fig.patches.append(rect_sidebar)
fig.text(0.82, 0.91, 'Filters & Parameters', fontsize=14, fontweight='bold', color=text_color)
fig.text(0.82, 0.88, 'Service Year', fontsize=12, color=subtext_color)
fig.text(0.82, 0.85, '☑ 2024   ☑ 2025   ☑ 2026', fontsize=13, color=tableau_blue)
fig.text(0.82, 0.80, 'Claim Status', fontsize=12, color=subtext_color)
fig.text(0.82, 0.77, '◉ All', fontsize=13, color=text_color)

fig.text(0.82, 0.72, 'Plan Type', fontsize=12, color=subtext_color)
fig.text(0.82, 0.69, '▼ (Multiple Values)', fontsize=13, color=text_color)
fig.text(0.82, 0.64, 'Region Selection', fontsize=12, color=subtext_color)
fig.text(0.82, 0.61, '▼ National', fontsize=13, color=text_color)

# Adding a Tableau-style Legends block in Sidebar
fig.text(0.82, 0.50, 'Status Legend', fontsize=13, fontweight='bold', color=subtext_color)
fig.text(0.82, 0.46, '■ Approved', fontsize=13, color=tableau_green)
fig.text(0.82, 0.43, '■ Denied', fontsize=13, color=tableau_red)
fig.text(0.82, 0.40, '■ Pending', fontsize=13, color=tableau_orange)
fig.text(0.82, 0.37, '■ In Process', fontsize=13, color='#B07AA1')

# ---- GRID LAYOUT (Main Area) ----
gs = gridspec.GridSpec(3, 3, height_ratios=[0.5, 2.7, 2.7], figure=fig)
gs.update(wspace=0.2, hspace=0.35, top=0.86, bottom=0.08, left=0.02, right=0.79)

def style_panel(ax, title):
    ax.set_facecolor(panel_color)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#D1D5D8')
    ax.spines['bottom'].set_color('#D1D5D8')
    ax.tick_params(colors=subtext_color)
    ax.set_title(title, loc='center', fontsize=14, fontweight='bold', color=text_color, pad=15)
    
    # Outer stroke simulating a distinct workbook container
    bbox = ax.get_position()
    pad = 0.015
    rect = Rectangle((bbox.x0 - pad, bbox.y0 - pad*1.2), bbox.width + pad*2, bbox.height + pad*2.6, 
                     transform=fig.transFigure, facecolor=panel_color, zorder=-1, edgecolor='#D1D5D8')
    fig.patches.append(rect)

# KPIs
def create_kpi(ax, title, value, color):
    ax.axis('off')
    ax.text(0.5, 0.70, title, fontsize=12, color=subtext_color, ha='center', transform=ax.transAxes)
    ax.text(0.5, 0.25, value, fontsize=36, fontweight='bold', color=color, ha='center', transform=ax.transAxes)
    
    bbox = ax.get_position()
    rect = Rectangle((bbox.x0, bbox.y0), bbox.width, bbox.height, 
                     transform=fig.transFigure, facecolor=panel_color, zorder=-1, edgecolor='#D1D5D8')
    fig.patches.append(rect)

ax1 = fig.add_subplot(gs[0, 0])
create_kpi(ax1, 'TOTAL CLAIM VOLUME', total_claims, tableau_blue)

ax2 = fig.add_subplot(gs[0, 1])
create_kpi(ax2, 'TOTAL AMOUNT PAID', total_paid, tableau_green)

ax3 = fig.add_subplot(gs[0, 2])
create_kpi(ax3, 'CLAIM REJECTION RATE', rejection_pct, tableau_red)

# Line Chart Trends
ax4 = fig.add_subplot(gs[1, :2])
monthly_spend = df_claims.groupby('month')['approved_amount'].sum().reset_index()
monthly_spend['month'] = monthly_spend['month'].dt.to_timestamp()
recent = monthly_spend.tail(18)
ax4.plot(recent['month'], recent['approved_amount'], color=tableau_blue, marker='o', linewidth=2.5, markersize=7)
ax4.fill_between(recent['month'], recent['approved_amount'], color=tableau_blue, alpha=0.08)
style_panel(ax4, 'MONTHLY MEDICAL SPEND ($)')
ax4.grid(axis='y', linestyle='-', color=grid_color)
ax4.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

# Horizontal Bar - Pareto
ax5 = fig.add_subplot(gs[1, 2])
reasons = df_claims[df_claims['claim_status'] == 'Denied']['rejection_reason'].value_counts()
reasons = reasons[reasons.index != 'None'].head(5)
y_pos = np.arange(len(reasons))
ax5.barh(y_pos, reasons.values[::-1], color=tableau_orange, height=0.7)
ax5.set_yticks(y_pos)
ax5.set_yticklabels(reasons.index[::-1])
style_panel(ax5, 'TOP 5 REJECTION CATEGORIES')
ax5.xaxis.grid(True, linestyle='-', color=grid_color)

# Area / Bar combination or Donut
ax6 = fig.add_subplot(gs[2, :2])
status_counts = df_claims.groupby([pd.Grouper(key='service_date', freq='M'), 'claim_status'])['claim_id'].count().unstack().tail(12)
dates_stack = status_counts.index
# Area chart simulation 
if 'Approved' in status_counts.columns:
    ax6.plot(dates_stack, status_counts['Approved'], color=tableau_green, label='Approved', linewidth=2)
if 'Denied' in status_counts.columns:
    ax6.plot(dates_stack, status_counts['Denied'], color=tableau_red, label='Denied', linewidth=2)
if 'Pending' in status_counts.columns:
    ax6.plot(dates_stack, status_counts['Pending'], color=tableau_orange, label='Pending', linewidth=2)
style_panel(ax6, 'VOLUME TREND BY LIFECYCLE STATUS (LAST 12 MONTHS)')
ax6.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax6.grid(axis='y', linestyle='-', color=grid_color)
ax6.legend(loc='upper left', frameon=False)

# Demographic Bar
ax7 = fig.add_subplot(gs[2, 2])
# Simulated distribution for demographic
specialty_cost = df_claims.groupby(df_claims.index % 5)['approved_amount'].sum() # pseudo specialty split
specialty_names = ['Cardiology', 'Orthopedics', 'General', 'Pediatrics', 'Neurology']
y_pos2 = np.arange(len(specialty_names))
custom_colors = [tableau_blue, '#76B7B2', '#E15759', '#F28E2B', '#59A14F']
ax7.barh(y_pos2, specialty_cost.values[::-1], color=custom_colors, height=0.7)
ax7.set_yticks(y_pos2)
ax7.set_yticklabels(specialty_names[::-1])
style_panel(ax7, 'MEDICAL SPEND BY SPECIALTY')
ax7.xaxis.grid(True, linestyle='-', color=grid_color)

# ---- BOTTOM WORKBOOK TABS ----
rect_tabs = Rectangle((0, 0), 1, 0.04, transform=fig.transFigure, facecolor='#EAEAEA', edgecolor='#D1D5D8', zorder=1)
fig.patches.append(rect_tabs)
fig.text(0.01, 0.01, 'Data Source      [ Executive DB ]      Operations      Pop Health', fontsize=11, fontweight='bold', color=text_color, zorder=2)

plt.savefig(out_file, dpi=250, bbox_inches='tight', facecolor=bg_color)
print("Ultra-Realistic Tableau Light-Theme Mockup Generated!")
