import pandas as pd 
import seaborn as sns 
from matplotlib.axes import Axes

from .utils import country_colors 
from ...utils.countries import european_countries_hl, european_countries

def plot_flights_zone_to_europe(ax : Axes, df : pd.DataFrame):

    zone_to_europe = df[df['trip_destination_co'].isin(
        european_countries
    )]

    zone_to_europe = zone_to_europe.groupby(['timestamp','trip_destination_co'])['passengers'].sum().reset_index(drop = False)
    zone_to_europe['highlighted'] = zone_to_europe['trip_destination_co'].isin(european_countries_hl)
    sns.lineplot(zone_to_europe[zone_to_europe['highlighted']], 
                 x = 'timestamp', y = 'passengers', hue = 'trip_destination_co', palette = country_colors)
    sns.lineplot(zone_to_europe[zone_to_europe['highlighted'] == False], 
                 x = 'timestamp', y = 'passengers', c = 'grey')
    ax.set_yscale('log')
