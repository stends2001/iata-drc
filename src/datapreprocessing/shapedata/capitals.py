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
    gdf.crs = crs_degrees
    return gdf

if __name__ == '__main__':
    pm = PathManager()
    
    raw_data = raw_capitals(pm.data / 'raw' / 'shapedata' / 'country-capital-lat-long-population.csv')
    pcd_data = preprocess_capitals(raw_data)
    save_gdf(pcd_data,
             pm.data / 'processed' / 'shapedata' / "shared" / "capitals.shp",
             )
