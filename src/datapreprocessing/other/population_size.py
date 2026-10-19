import pandas as pd 
from pathlib import Path 

from ...utils import PathManager
from ...utils.drc_mappings import healthzones_populationdata
from ..shapedata.countries.dataloaders import _load_uga_adm2
from ...utils.region_mappings import uga_adm2_drc_namesakes

def _adjust_doubles_population_size(df : pd.DataFrame) -> pd.DataFrame:
    mapping= {
            ("Nord-Ubangi", "Bili")     : "bili (nord-ubangi)",
            ("Bas-Uele", "Bili")        : "bili (bas-uele)",
            ("Tshopo", "Lubunga")       : "lubunga (tshopo)",
            ("Kasaï-Central", "Lubunga"): "lubunga (kasaï-central)",
        }
    for (province, healthzone), replacement in mapping.items():
        mask = (df["province"] == province) & (df["healthzone"] == healthzone)
        df.loc[mask, "healthzone"] = replacement    

    return df

def load_raw_population_data_drc(path : Path) -> pd.DataFrame:
    """load raw population data"""
    return pd.read_excel(path)

def load_raw_population_data_uga(path : Path) -> pd.DataFrame:
    return pd.read_excel(path, sheet_name = None) 

def process_population_data_drc(df : pd.DataFrame) -> pd.DataFrame:
    """process population data"""
    df['healthzone']= df['Zone de sante'].replace(healthzones_populationdata)
    df              = _adjust_doubles_population_size(df.rename(columns = {'Province':'province','Territoire':'territoire'}))    
    df              = df.copy().rename(columns = {'Population 2024 ' : 'population'})
    df              = df[['population','healthzone']]
    df['healthzone']= df['healthzone'].str.lower()
    return df

def process_population_data_uga(df : pd.DataFrame) -> pd.DataFrame:
    path_manager = PathManager()
    adm2codes = _load_uga_adm2(path_manager.data / 'raw' / 'shapedata' / 'uganda' / 'uga_admin2.shp', True)
    
    popsize = pd.merge(adm2codes[['shapeName','adm2_pcode']],
        df['uga_admpop_adm2_2023'],
        left_on= 'adm2_pcode', right_on = 'ADM2_PCODE')
    popsize = popsize[['T_TL','shapeName']].rename(columns = {'T_TL' : 'population', 'shapeName' : 'district'})
    popsize['district'] = popsize['district'].str.lower()
    popsize['district'] = popsize['district'].replace(uga_adm2_drc_namesakes)
    
    return popsize


