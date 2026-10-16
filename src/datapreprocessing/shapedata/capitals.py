import geopandas as gpd 
import pandas as pd
from pathlib import Path

from ..utils import save_df, save_gdf
from ...utils import PathManager
from ...utils.constants import crs_degrees

capital_mappings = {
    'democratic republic of the congo'    : 'drc',
    'south sudan'                         : 'south_sudan',
    'central african republic'            : 'caf',
    'united republic of tanzania'         : 'tanzania'    
}

def raw_capitals(path : Path) -> gpd.GeoDataFrame:
    """
    Load raw data on capitals: interested in longitude, latitutde and names.
    """
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
    """
    Preprocess capital data
    """
    gdf['country'] = gdf['country'].str.lower()
    gdf['country'] = gdf['country'].replace(capital_mappings)
    gdf['city'] = gdf['city'].str.lower()
    gdf.crs = crs_degrees
    return gdf