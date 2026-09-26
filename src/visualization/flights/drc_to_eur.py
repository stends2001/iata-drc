import pandas as pd 
import seaborn as sns
from matplotlib.axes import Axes 

from .utils import country_colors
from ...utils.countries import european_countries, european_countries_hl

def plot_flights_drc_to_europe(ax : Axes, df : pd.DataFrame):
    drc_to_europe = df[df['trip_destination_co'].isin(
        european_countries
    )]
    drc_to_europe = drc_to_europe[drc_to_europe['trip_origin_co'] == 'drc']
    drc_to_europe = drc_to_europe.groupby(['timestamp','trip_destination_co'])['passengers'].sum().reset_index(drop = False)
    drc_to_europe['highlighted'] = drc_to_europe['trip_destination_co'].isin(european_countries_hl)

    sns.lineplot(drc_to_europe[drc_to_europe['highlighted']], 
                 x = 'timestamp', y = 'passengers', hue = 'trip_destination_co', 
                 palette = country_colors)
    
    sns.lineplot(drc_to_europe[drc_to_europe['highlighted'] == False], 
                 x = 'timestamp', y = 'passengers', c = 'grey')
    ax.set_yscale('log')
