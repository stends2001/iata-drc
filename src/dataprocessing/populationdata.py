from pathlib import Path 
import pandas as pd

from ..utils.drc_mappings import mapping_pop

def load_population_data(rawpath : Path) -> pd.DataFrame:
    """load raw population data"""
    return pd.read_excel(rawpath / 'drc-hpc-projection-population-2024.xlsx')

def process_population_data(df : pd.DataFrame) -> pd.DataFrame:
    """process population data"""
    df['healthzone']= df['Zone de sante'].replace(mapping_pop)
    df              = df.copy().rename(columns = {'Population 2024 ' : 'population'})
    df              = df[['population','healthzone']]
    df['healthzone']= df['healthzone'].str.lower()
    return df