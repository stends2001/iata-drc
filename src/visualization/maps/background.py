import matplotlib.pyplot as plt 
from matplotlib.axes import Axes
import geopandas as gpd
from shapely.geometry import box

from ...dataprocessing.shapedata.shapedata_containers import Countryshp

from .utils import geomap_args, box_coordinates
from ...utils.countries import countries_background
from ...utils.airports import airports_zone1

def plot_geography_map(ax : Axes,
                       shapedata : dict[str, Countryshp],
                       airport_shp : gpd.GeoDataFrame | None = None):
    """ 
    Make a 'geography-style-map'. Background countries come in grey, other countries
    highlighted with capitals. Optionally with airport shapefile.
    """
    # axis limits
    x_min, x_max = box_coordinates['background']['x']
    y_min, y_max = box_coordinates['background']['y']
    map_box      = box(x_min, y_min, x_max, y_max)

    # set facecolor; sea blue
    ax.set_facecolor(**geomap_args['sea'])

    for country_name, country_shape in shapedata.items():

        gdf = country_shape.shp

        # Level 1: country shape

        # background country: only national adm0
        if country_name in countries_background:
            gdf.plot(
                ax = ax,
                **geomap_args['background_countries']
            )

        # otherwise: both national and first lvl adm
        else:
            for admin_lvl in ['adm0','adm1']:

                sub_section = gdf[gdf['admin_level'] == admin_lvl] 
                                
                sub_section.plot(
                    ax=ax,
                    **geomap_args[admin_lvl]
                )

        # Level 2: capital

        for _, row in gdf[gdf['admin_level'] == 'adm0'].iterrows():

            clipped_geometry = row.geometry.intersection(map_box)

            if not clipped_geometry.is_empty:
                point = clipped_geometry.representative_point()

                # put in name of country
                ax.text(
                    point.x,
                    point.y,
                    country_name.upper(),
                    ha="center",
                    va="center",
                    fontsize=8 if country_name in countries_background else 11,
                    fontweight="bold"
                )

        # plot country capital
        country_shape.capital.plot(
            ax = ax,
            **geomap_args['capital']
        )

    # if airport shapefile supplied, plot it
    if airport_shp is not None:
        airport_shp[airport_shp['code'].isin(airports_zone1)].plot(ax = ax, **geomap_args['airport'])

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)