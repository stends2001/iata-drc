from pathlib import Path 
import pandas as pd 
import geopandas as gpd

from ..utils.constants import crs_degrees

def save_df(df : pd.DataFrame, path : Path) -> None:
    df.to_csv(path, 
              encoding = 'UTF-8',
              index=False)

def save_gdf(gdf : gpd.GeoDataFrame, path : Path) -> None:
    gdf = gdf.to_crs(crs_degrees)

    gdf.to_file(
        path,
        driver="ESRI Shapefile",
        encoding="UTF-8"
    )    
    
from shapely.geometry.polygon import orient
from shapely.geometry import Polygon, MultiPolygon
def fix_winding(geom):
    if geom is None or geom.is_empty:
        return geom

    if geom.geom_type == "Polygon":
        return orient(geom, sign=-1.0)

    if geom.geom_type == "MultiPolygon":
        return MultiPolygon([
            orient(poly, sign=-1.0)
            for poly in geom.geoms
        ])

    return geom