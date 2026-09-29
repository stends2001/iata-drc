from matplotlib.axes import Axes 
import geopandas as gpd

from ..utils import airport_colors

def add_catchment_areas(ax : Axes,
                        catchment_areas : gpd.GeoDataFrame,
                        hz_catchments : gpd.GeoDataFrame,
                        airports_shp : gpd.GeoDataFrame):
    
    hz_catchments.plot(column = 'p_main', 
                         cmap = 'Blues', 
                         vmin = 0, vmax= 1, 
                         ax = ax, 
                         legend = True, 
                         legend_kwds = {
                             'orientation' : 'horizontal', 
                             'shrink' : 0.6, 'pad' : 0.02}
                             )

    catchment_areas.boundary.plot(ax=ax, color='black', linewidth=0.7)

    airports_shp.plot(
        ax=ax,
        edgecolor="black",
    )

    # Markers
    ax.scatter(
        airports_shp.geometry.x,
        airports_shp.geometry.y,
        color="darkorange",
        edgecolor = 'black',
        s=30,
        zorder=5,
    )

    # Labels
    for idx, row in airports_shp.iterrows():
        ax.annotate(
            row["code"],
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


def plot_highlighted_airports(ax: Axes, airports_shp : gpd.GeoDataFrame):

    
    colors = airports_shp["code"].map(airport_colors).fillna("lightgray")

    airports_shp.plot(
        ax=ax,
        markersize = 75,
        edgecolor = 'black',
        color=colors,
    )

    for idx, row in airports_shp.iterrows():
        if row['code'] in airport_colors.keys():
            ax.annotate(
                row["code"],
                xy=(row.geometry.x, row.geometry.y),       # marker position
                xytext=(10, 1),                              # text offset in points
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