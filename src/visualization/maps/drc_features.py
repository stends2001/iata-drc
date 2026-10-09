from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.colors import LogNorm
import matplotlib.pyplot as plt
import numpy as np
import geopandas as gpd 
import pandas as pd
from matplotlib_scalebar.scalebar import ScaleBar
from ...utils.airports import airports_drc
from ...utils.constants import crs_metres

def add_popsize_to_map(ax : Axes, 
                       fig: Figure, 
                       gdf: gpd.GeoDataFrame,
                       scalebar : bool = True):
    """ 
    To a given ax and fig, add population size per health zone.
    Ensure that columns 'population' and 'geometry' are present.
    """
    gdf['population_div'] = gdf['population'] / 1000

    gdf = gdf.to_crs(crs_metres)
    norm = plt.Normalize(
        vmin=gdf["population_div"].min(),
        vmax=gdf["population_div"].max()    
    )

    gdf.plot(
        ax=ax,
        column="population_div",
        cmap="Blues",
        norm = norm,
        legend=False
    )    

    sm = plt.cm.ScalarMappable(
        cmap="Blues",
        norm=norm
    )

    cbar = fig.colorbar(
        sm,
        ax=ax,
        orientation="horizontal",
        fraction=0.046,
        pad=0.04
    )    

    cbar.set_label("Population [x 1000]")

    if scalebar:
        ax.add_artist(ScaleBar(1, units="m", fixed_value=500, fixed_units="km", location="lower left"))    

def add_popdens_to_map(ax : Axes, 
                       fig: Figure, 
                       gdf: gpd.GeoDataFrame,
                       scalebar : bool = True):
    """ 
    To a given ax and fig, add population density per health zone.
    Ensure that columns 'population_density' and 'geometry' are present.
    """    
    gdf = gdf.to_crs(crs_metres)    
    norm = LogNorm(
        vmin=gdf["population_density"].min(),
        vmax=gdf["population_density"].max()
    )

    gdf.plot(
        ax=ax,
        column="population_density",
        cmap="Greens",
        norm = norm,
        legend=False
    )    

    sm = plt.cm.ScalarMappable(
        cmap="Greens",
        norm=norm
    )

    cbar = fig.colorbar(
        sm,
        ax=ax,
        orientation="horizontal",
        fraction=0.046,
        pad=0.04
    )    

    cbar.set_label("Population density [1 000 / km2]")

    if scalebar:
        ax.add_artist(ScaleBar(1, units="m", fixed_value=500, fixed_units="km", location="lower left"))       

def add_cases_to_map(ax : Axes, 
                     fig : Figure, 
                     gdf: gpd.GeoDataFrame,
                     scalebar : bool = True):
    """ 
    To a given ax and fig, add cases per health zone.
    Ensure that columns 'cases_cumulative_corrected' and 'geometry' are present.
    """    
    gdf = gdf.to_crs(crs_metres)
    data = gdf.dropna(subset = ['cases_cumulative_corrected'])

    norm = plt.Normalize(
        vmin=data['cases_cumulative_corrected'].min(),
        vmax=data['cases_cumulative_corrected'].max()
    )

    gdf.plot(
        ax=ax,
        column='cases_cumulative_corrected',
        edgecolor = 'black',
        linewidth = 0.1,
        cmap="Reds",
        norm = norm,
        legend=False
    )    

    sm = plt.cm.ScalarMappable(
        cmap="Reds",
        norm=norm
    )

    cbar = fig.colorbar(
        sm,
        ax=ax,
        orientation="horizontal",
        fraction=0.046,
        pad=0.04
    )    

    cbar.set_label("Cases")    
    if scalebar:
        ax.add_artist(ScaleBar(1, units="m", fixed_value=500, fixed_units="km", location="lower left"))       

def add_aiports_on_map(ax : Axes, 
                        fig : Figure,
                        travel_data : pd.DataFrame,
                        airports_shapefile : gpd.GeoDataFrame,
                        scalebar : bool = True
                        ):
    """ 
    To a given ax and fig, add airports.
    Please use zone_out for travel_data and iata_airports for airports_shapefile
    """  
    airports_shapefile = airports_shapefile.to_crs(crs_metres)
    zone_out_drc_airports = (
        travel_data[travel_data['trip_origin_ap'].isin(airports_drc)]
        .assign(domestic=lambda d: d['trip_origin_co'] == d['trip_destination_co'])
        )

    domestic_pct = (
        zone_out_drc_airports
        .assign(domestic_passengers=lambda d: d['passengers'].where(d['domestic'], 0))
        .groupby('trip_origin_ap', as_index=False)
        .agg(total_passengers=('passengers', 'sum'),
            domestic_passengers=('domestic_passengers', 'sum'))
    )
    domestic_pct['domestic_share'] = 100 * domestic_pct['domestic_passengers'] / domestic_pct['total_passengers']
    domestic_pct['international_share'] = 100 - domestic_pct['domestic_share']

    p = np.log10(domestic_pct['total_passengers'].clip(lower=1))

    domestic_pct['marker_size'] = 5 + p**2 * 7

    drc_airports_shp = airports_shapefile[airports_shapefile['code'].isin(airports_drc)]
    gdf = gpd.GeoDataFrame(domestic_pct.merge(drc_airports_shp, left_on='trip_origin_ap', right_on='code'),
                        geometry='geometry', crs=drc_airports_shp.crs)


    norm1 = plt.Normalize(
        vmin=0,
        vmax=100
    )

    cmap = 'PuOr'

    gdf.plot(column='international_share', markersize=gdf['marker_size'].to_numpy(),
            cmap=cmap, vmin=0, vmax=100, edgecolor='black', ax=ax, norm = norm1)    

    sm = plt.cm.ScalarMappable(
        cmap=cmap,
        norm=norm1
    )

    cbar = fig.colorbar(
        sm,
        ax=ax,
        orientation="horizontal",
        fraction=0.046,
        pad=0.04
    )    
    cbar.set_label("International share [%]")    
    if scalebar:
        ax.add_artist(ScaleBar(1, units="m", fixed_value=500, fixed_units="km", location="lower left"))       

def add_road_network_on_map(ax : Axes, gdf: gpd.GeoDataFrame):
    gdf = gdf.to_crs(crs_metres)
    gdf["highway"] = gdf["highway"].str.replace("_link", "", regex=False)
    keep = ["trunk","primary","secondary","tertiary"]
    roads = gdf[gdf["highway"].isin(keep)].explode(index_parts=False)


    drc_network_map_args = {
        'primary' : {'linewidth' : 1, 
                    'edgecolor' : 'black'},
        'secondary': {'linewidth' : 0.75, 
                    'edgecolor' : 'black'},
        'tertiary' : {'linewidth' : 0.5, 
                    'edgecolor' : 'black'},
        'trunk'     : {'linewidth' : 0.1, 
                    'edgecolor' : 'black'}

    }

    # 3. Quick map
    for road_type in keep:

        roads[roads['highway'] == road_type].plot(**drc_network_map_args[road_type], ax = ax, zorder = 1)    


def add_cases_and_airports_on_map(ax : Axes, fig : Figure, gdf: gpd.GeoDataFrame, airports : gpd.GeoDataFrame, scalebar : bool = True):

    gdf = gdf.to_crs(crs_metres)
    data = gdf.dropna(subset = ['cases_cumulative_corrected'])    

    norm = LogNorm(
        vmin=2,
        vmax=data['cases_cumulative_corrected'].max()
    )


    gdf.plot(
        ax=ax,
        column='cases_cumulative_corrected',
        edgecolor = 'black',
        linewidth = 0.1,
        cmap="Reds",
        norm = norm,
        legend=False
    )    

    sm = plt.cm.ScalarMappable(
        cmap="Reds",
        norm=norm
    )

    cbar = fig.colorbar(
        sm,
        ax=ax,
        orientation="horizontal",
        fraction=0.046,
        pad=0.04
    )    

    cbar.set_label("Cases")    

    aps = airports[airports['code'].isin(airports_drc)].to_crs(crs_metres)
    # Base polygons
    aps.plot(
        ax=ax,
        edgecolor="black",
    )

    # Markers
    ax.scatter(
        aps.geometry.x,
        aps.geometry.y,
        color="darkgreen",
        s=30,
        zorder=5,
    )

    # Labels
    for idx, row in aps.iterrows():
        apscode = row['code']

        label =apscode+" *" if apscode in ['GOM', 'BUX'] else apscode

        ax.annotate(
            text = label,
            xy=(row.geometry.x, row.geometry.y),       # marker position
            xytext=(8, 8),                              # text offset in points
            textcoords="offset points",
            fontsize=10,
            zorder=6,
            bbox=dict(
                boxstyle="round,pad=0.3",
                facecolor="white",
                edgecolor="black",
                alpha=0.8,
            ),
        )

    if scalebar:
        ax.add_artist(ScaleBar(1, units="m", fixed_value=500, fixed_units="km", location="lower left"))           