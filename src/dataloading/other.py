import geopandas as gpd 
import pandas as pd 

from ..utils import PathManager

pm = PathManager()

def load_population_drc() -> pd.DataFrame:
    return pd.read_csv(pm.data / 'processed' / 'other' / 'population_drc.csv')    

def load_population_uga() -> pd.DataFrame:
    return pd.read_csv(pm.data / 'processed' / 'other' / 'population_uga.csv')    