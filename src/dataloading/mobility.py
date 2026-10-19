import geopandas as gpd 
import pandas as pd 

from ..utils import PathManager


pm = PathManager()

def load_iata_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    zone_in = pd.read_csv(pm.data / 'processed' / 'mobility' / 'iata_zone_in.csv', parse_dates= ['timestamp'])
    zone_out = pd.read_csv(pm.data / 'processed' / 'mobility' / 'iata_zone_out.csv', parse_dates= ['timestamp'])    
    return zone_in, zone_out