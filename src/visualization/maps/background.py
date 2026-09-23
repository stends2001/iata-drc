from matplotlib.axes import Axes
import geopandas as gpd

from .utils import geomap_args

def plot_drc_skeleton(ax : Axes,
                      shp : gpd.GeoDataFrame,
                      background_empty: bool = False):
    """
    plot skeleton of DRC on ax: that is, national outline and province outline.
    """
    for admin_lvl in ['adm0','adm1']:

        sub_section = shp[shp['admin_level'] == admin_lvl]
        map_args    = geomap_args[admin_lvl]

        if background_empty:
            map_args['facecolor'] = 'none'

        sub_section.plot(
                ax=ax,
                **map_args
            )    
        
        ax.set_xticks([])
        ax.set_yticks([])    