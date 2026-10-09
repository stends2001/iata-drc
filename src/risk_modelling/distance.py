import pandas as pd 
import geopandas as gpd 
from typing import Literal

from ..utils.constants import crs_metres

def get_distance_matrix(gdf_hz: gpd.GeoDataFrame,
                        gdf_ap : gpd.GeoDataFrame,
                        mode : Literal['euclidian-distance']    
                        ) -> pd.DataFrame:
    """
    Get distance matrix that represents the distance between health zone and airports.
    Since this is a static matrix, no temporal-mode here.

    Parameters
    ----------
    gdf_hz : gpd.GeoDataFrame
        shapefile of health zones.
    gdf_ap : gpd.GeoDataFrame
        shapefile of airports to be taken into consideration.
    mode : Literal['euclidian-distance']
        mode on which to base distance.
    """
    gdf_hz = gdf_hz.rename(columns = {'name':'healthzone'}).to_crs(crs_metres)
    gdf_hz = gdf_hz.sort_values(by = 'healthzone')
    region_centroids = gdf_hz.set_index('healthzone').geometry.centroid
    airports         = gdf_ap.set_index('airport')

    match mode:

        case 'euclidian-distance':

            # km, zone x airport
            distance_mtx     = pd.DataFrame({
                                a: region_centroids.distance(g) / 1000 for a, g in airports.geometry.items()
                                })    

        case _:
            raise ValueError('invalid value for mode. Currently supported: euclidian-distance')
        
    return distance_mtx