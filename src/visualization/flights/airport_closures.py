import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.axes import Axes

from ..utils import airport_colors

GREY = '#a3a29c'


def monthly_departures_arrivals(zone_in: pd.DataFrame, zone_out: pd.DataFrame, airports: list[str]) -> pd.DataFrame:
    """
    Tidy table per airport and month:
      departures        = all trips starting at the airport (domestic + international), from zone_out
      domestic_arrivals = domestic trips ending at the airport, from zone_in
    """
    dep = (zone_out[(zone_out['trip_origin_co'] == 'drc') & zone_out['trip_origin_ap'].isin(airports)]
           .groupby(['trip_origin_ap', 'timestamp'])['passengers'].sum()
           .rename_axis(['airport', 'timestamp']).rename('departures'))
    arr = (zone_in[(zone_in['trip_origin_co'] == 'drc') & (zone_in['trip_destination_co'] == 'drc')
                   & (zone_in['trip_origin_ap'] != zone_in['trip_destination_ap'])
                   & zone_in['trip_destination_ap'].isin(airports)]
           .groupby(['trip_destination_ap', 'timestamp'])['passengers'].sum()
           .rename_axis(['airport', 'timestamp']).rename('domestic_arrivals'))
    return pd.concat([dep, arr], axis=1).fillna(0).reset_index()


def plot_rerouting_check(df: pd.DataFrame, airports: list[str], year: int = 2026,
                         closures: list[tuple[str, str]] = [('2026-05-23', '2026-06-01'), ('2026-06-08', '2026-08-31')],
                         closure_label: str = 'Bunia closed to commercial flights'):
    """
    Small multiples: one column per airport, rows = departures / domestic arrivals.
    Coloured line = `year`, grey line = same months one year earlier (seasonal baseline).
    Shaded = Bunia closure periods. Each panel has its own y-scale.
    """
    fig, axes = plt.subplots(2, len(airports), figsize=(3.2 * len(airports), 5.5), sharex=True)
    months = pd.date_range(f'{year}-01-01', f'{year}-08-01', freq='MS')

    for j, ap in enumerate(airports):
        d = df[df['airport'] == ap].set_index('timestamp')
        col = airport_colors.get(ap, '#52514e')
        for i, (var, lab) in enumerate([('departures', 'Departures'), ('domestic_arrivals', 'Domestic arrivals')]):
            ax: Axes = axes[i, j]
            now  = d[var].reindex(months, fill_value=0)
            prev = d[var].reindex(months - pd.DateOffset(years=1), fill_value=0)
            prev.index = months                                         # align last year onto this year's months

            for start, end in closures:
                ax.axvspan(pd.Timestamp(start), pd.Timestamp(end), color='#e1e0d9', zorder=0, lw=0)
            mid = months + pd.Timedelta(days=14)                        # monthly totals drawn mid-month
            ax.plot(mid, prev.values, color=GREY, lw=1.5, marker='o', ms=3, label=str(year - 1))
            ax.plot(mid, now.values, color=col, lw=2, marker='o', ms=4, label=str(year))

            ax.set_ylim(bottom=0)
            ax.xaxis.set_major_locator(mdates.MonthLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
            ax.tick_params(axis='x', labelsize=8, rotation=0)
            ax.tick_params(axis='y', labelsize=8)
            ax.grid(axis='y', color='#e1e0d9', lw=0.6)
            for s in ['top', 'right']:
                ax.spines[s].set_visible(False)
            if i == 0:
                ax.set_title(ap, loc='left', fontweight='bold', color=col)
            if j == 0:
                ax.set_ylabel(f'{lab}\n(passengers / month)', fontsize=9)

    # one shared legend
    handles = [plt.Line2D([], [], color='#52514e', lw=2, marker='o', ms=4, label=f'{year}'),
               plt.Line2D([], [], color=GREY, lw=1.5, marker='o', ms=3, label=f'{year - 1} (same month)'),
               plt.Rectangle((0, 0), 1, 1, color='#e1e0d9', label=closure_label)]
    fig.legend(handles=handles, loc='lower center', ncol=3, frameon=False, bbox_to_anchor=(0.5, -0.02))
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    return fig, axes