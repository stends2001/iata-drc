"""
Get capitals geometries
"""

import pandas as pd 
import geopandas as gpd
from pathlib import Path
from ...utils.countries import capital_mappings

def load_capitals(path : Path) -> gpd.GeoDataFrame:
    capitals_data_raw  = pd.read_csv(path)

    capitals_data_raw["geometry"] = gpd.points_from_xy(
        capitals_data_raw["Longitude"], capitals_data_raw["Latitude"]

        )    
    capitals_data = gpd.GeoDataFrame(
        capitals_data_raw.copy()
        # rename columns
        .rename(columns = {'Country'        : 'country', 
                           'Capital City'   : 'city'})
        # drop columns
        .drop(columns = ['Population', 'Capital Type','Latitude','Longitude'])
        )
    return capitals_data 

def preprocess_capitals(gdf : gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    gdf['country'] = gdf['country'].str.lower()
    gdf['country'] = gdf['country'].replace(capital_mappings)
    gdf['city'] = gdf['city'].str.lower()
    return gdf