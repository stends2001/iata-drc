from pathlib import Path 
import pandas as pd

from .shapedata.uganda import get_adm2_uganda_shp
from ..utils import PathManager
from ..utils.drc_mappings import mapping_pop
from .adjust_double_healthzones import adjust_doubles_population_size

from ..utils.drc_mappings import uganda_namesakes_drc

def load_population_data(rawpath : Path) -> pd.DataFrame:
    """load raw population data"""
    return pd.read_excel(rawpath / 'drc-hpc-projection-population-2024.xlsx')

def process_population_data(df : pd.DataFrame) -> pd.DataFrame:
    """process population data"""
    df['healthzone']= df['Zone de sante'].replace(mapping_pop)
    df = adjust_doubles_population_size(df.rename(columns = {'Province':'province','Territoire':'territoire'}))    
    df              = df.copy().rename(columns = {'Population 2024 ' : 'population'})
    df              = df[['population','healthzone']]
    df['healthzone']= df['healthzone'].str.lower()
    return df

def get_population_data_uganda() -> pd.DataFrame:
    adm2codes = get_adm2_uganda_shp(True)
    uganda_pop_raw = pd.read_excel(PathManager().data/'raw'/ 'shapedata'/'uganda'/'uga_admpop_2023.xlsx', sheet_name = None) 
    popsize = pd.merge(adm2codes[['shapeName','adm2_pcode']],
        uganda_pop_raw['uga_admpop_adm2_2023'],
        left_on= 'adm2_pcode', right_on = 'ADM2_PCODE')
    popsize = popsize[['T_TL','shapeName']].rename(columns = {'T_TL' : 'population', 'shapeName' : 'adm2'})
    popsize['adm2'] = popsize['adm2'].str.lower()
    popsize['adm2'] = popsize['adm2'].replace(uganda_namesakes_drc)
    
    return popsize