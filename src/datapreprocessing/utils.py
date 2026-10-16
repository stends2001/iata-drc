from pathlib import Path 
import pandas as pd 
import geopandas as gpd

from ..utils.constants import crs_degrees

def save_df(df : pd.DataFrame, path : Path) -> None:
    df.to_csv(path, 
              encoding = 'UTF-8')

def save_gdf(gdf : gpd.GeoDataFrame, path : Path) -> None:
    gdf = gdf.to_crs(crs_degrees)

    gdf.to_file(
        path,
        driver="ESRI Shapefile",
        encoding="UTF-8"
    )    