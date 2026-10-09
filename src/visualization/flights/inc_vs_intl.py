import pandas as pd 
import matplotlib.pyplot as plt 
from matplotlib.axes import Axes
from ..utils import airport_colors 


def plot_incidence_vs_international_passengers(ax : Axes, 
                                               flights_intl : pd.DataFrame,
                                               incidence : pd.DataFrame):
    START = pd.Timestamp('2026-05-01')                                   # outbreak period
    cols  = [m for m in flights_intl.columns if pd.Timestamp(m) >= START]

    
    Im  = incidence.reindex(index=flights_intl.index, columns=flights_intl.columns, fill_value=0)
    sc = pd.DataFrame({
        'intl_per_month': flights_intl[cols].mean(axis=1),              # mean international departures per month
        'peak_incidence': Im[cols].max(axis=1),                        # peak catchment incidence (per 100k)
    })
    is_colored = sc.index.isin(airport_colors)

    # Grey points underneath
    ax.scatter(
        sc.loc[~is_colored, 'intl_per_month'] + 1,
        sc.loc[~is_colored, 'peak_incidence'],
        s=70,
        color='#a3a29c',
        edgecolor='#fcfcfb',
        linewidth=2,
        zorder=3
    )

    # Colored points on top
    ax.scatter(
        sc.loc[is_colored, 'intl_per_month'] + 1,
        sc.loc[is_colored, 'peak_incidence'],
        s=70,
        color=sc.loc[is_colored].index.map(airport_colors),
        edgecolor='#fcfcfb',
        linewidth=2,
        zorder=4
    )
    for a, r in sc.iterrows():
        ax.annotate(a, (r['intl_per_month'] + 1, r['peak_incidence']), xytext=(6, 4),
                    textcoords='offset points', fontsize=9, color='#52514e')

    ax.set_xscale('log')
    ax.set_xlabel('International departures per month')
    ax.set_ylabel('Peak catchment incidence')
    ax.set_title('Catchment incidence and international traffic sit at different airports', loc='left', fontweight='bold')
    ax.grid(color='#e1e0d9', linewidth=0.6)
    for s in ['top', 'right']:
        ax.spines[s].set_visible(False)