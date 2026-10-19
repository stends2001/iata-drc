import pandas as pd 
import geopandas as gpd 
from typing import Literal
import numpy as np

from ..utils.constants import crs_metres, crs_degrees

DistanceMode = Literal['euclidian-distance', 'great-circle']

EARTH_RADIUS_KM = 6371.0088


def _haversine_km(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(np.radians, (lon1, lat1, lon2, lat2))
    a = np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
    return 2 * EARTH_RADIUS_KM * np.arcsin(np.sqrt(a))


def get_distance_matrix(gdf_units: gpd.GeoDataFrame,
                        gdf_airports : gpd.GeoDataFrame,
                        mode : DistanceMode,
                        ) -> pd.DataFrame:
    """
    Get distance matrix that represents the distance between health zone and airports.
    Since this is a static matrix, no temporal-mode here.

    Parameters
    ----------
    gdf_hz : gpd.GeoDataFrame
        shapefile of health zones.
    gdf_ap : gpd.GeoDataFrame
        shapefile of airports to be taken into consideration (column 'airport').
    mode :
        'euclidian-distance' : straight line in crs_metres (EPSG:6933 is equal-AREA, so distances are
                               distorted by up to ~14 % in this region; kept for backward compatibility)
        'great-circle'       : haversine distance in km (recommended straight-line distance)
        'travel-time'        : hours over the cheapest route on a friction surface
                               (MAP motorized friction surface; needs `friction_path`)
    friction_path :
        path to the friction GeoTIFF (only for 'travel-time').

    Returns zone x airport (km, or hours for 'travel-time'); index = health zone (sorted), columns = airport.
    """
    gdf_units = gdf_units.sort_values(by = 'unit')
    region_centroids = gdf_units.set_index('unit').geometry.centroid
    airports         = gdf_airports.set_index('airport')

    match mode:

        case 'euclidian-distance':

            # km, zone x airport
            distance_mtx     = pd.DataFrame({
                                a: region_centroids.distance(g) / 1000 for a, g in airports.to_crs(crs_metres).geometry.items()
                                })

        case 'great-circle':
            c  = region_centroids.to_crs(crs_degrees)
            ap = airports.to_crs(crs_degrees).geometry
            distance_mtx = pd.DataFrame({
                                a: _haversine_km(c.x.values, c.y.values, g.x, g.y) for a, g in ap.items()
                                }, index=c.index)

        case _:
            raise ValueError('invalid value for mode. Supported: euclidian-distance, great-circle')

    return distance_mtx