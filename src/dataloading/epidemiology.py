import geopandas as gpd 
import pandas as pd 

from ..utils import PathManager


pm = PathManager()

def load_casedata() -> pd.DataFrame:
    return pd.read_csv(pm.data / 'processed' / 'epidemiology' / 'cases.csv', parse_dates= ['timestamp'])    