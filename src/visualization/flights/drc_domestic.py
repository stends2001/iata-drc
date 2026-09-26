from matplotlib.axes import Axes 
import pandas as pd

def plot_domestic_international_flights_drc(ax : Axes, df : pd.DataFrame):

    drc_intl            = df[df['trip_origin_co'] == 'drc']
    drc_intl.loc[drc_intl['trip_destination_co'] == 'drc', 'domestic'] = 'domestic'
    drc_intl.loc[drc_intl['trip_destination_co'] != 'drc', 'domestic'] = 'international'

    drc_intl = drc_intl.groupby(['timestamp',
                                'domestic'])['passengers'].sum().reset_index(drop = False)


    drc_intl['date'] = drc_intl['timestamp'].dt.date


    table = drc_intl.pivot_table(index="date", columns="domestic", values="passengers", aggfunc="sum")
    table.plot(kind="bar", stacked=True, ax=ax)

    ax.set_xlabel("")
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.025), ncol=2, fancybox=True, shadow=True);