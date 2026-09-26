from matplotlib.axes import Axes
import geopandas as gpd

from .utils import geomap_args
from ...utils.constants import crs_metres

def plot_drc_skeleton(ax : Axes,
                      shp : gpd.GeoDataFrame,
                      background_empty: bool = False,
                      adm1 : bool = True):
    """
    plot skeleton of DRC on ax: that is, national outline and province outline.
    """
    adms = ['adm0', 'adm1'] if adm1 else ['adm0']
    shp = shp.to_crs(crs_metres)
    for admin_lvl in adms:

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