from pathlib import Path 
import pandas as pd

from ..utils.drc_mappings import mapping_cases

def load_case_data(rawpath : Path) -> pd.DataFrame:
    """raw case data"""
    df = pd.read_csv(rawpath / 'cases.csv', header = None)
    df.rename(columns = {0 : 'healthzone', 1 : 'date', 2 : 'cases_cumulative'}, inplace = True)
    return df

def process_case_data(raw_data : pd.DataFrame):
    """process case data"""
    pcd_data = raw_data.copy()

    # ================================
    # = 1. typos that need to be fixed
    
    # clean up single date error namely "2026-06-25]"
    pcd_data['date'] = pcd_data['date'].replace({'2026-06-25]' : '2026-06-25'})

    # clean up single cases error namely "17-" (surrounded by '17' and '17')
    pcd_data['cases_cumulative'] = pcd_data['cases_cumulative'].replace({'17-' : '17'})    

    # ========================================
    # = 2. some low-level data transformations

    # proper timestamp
    pcd_data['date'] = pd.to_datetime(pcd_data['date'], format = '%Y-%m-%d', errors = 'coerce')

    # map health zones
    pcd_data['healthzone'] = pcd_data['healthzone'].replace(mapping_cases)

    # lower case health zones
    pcd_data['healthzone'] = pcd_data['healthzone'].str.lower()

    # ===================
    # = 3. DECISIONS made

    # DECISION 1: drop rows where healthzone is not known
    pcd_data = pcd_data.dropna(subset = ['healthzone'])

    # DECISION 2: forward fill cumulative cases (got some NaNs)
    pcd_data = pcd_data.sort_values(["healthzone", "date"])
    pcd_data['cases_cumulative'] = pd.to_numeric(pcd_data['cases_cumulative'], errors='coerce')
    pcd_data["cases_cumulative"] = pcd_data.groupby("healthzone")["cases_cumulative"].ffill()  

    # DECISION 3: remove healthzone 'jiba': only got NaNs for its 4 entries
    pcd_data = pcd_data[pcd_data['healthzone'] != 'jiba']

    pcd_data['cases_cumulative'] = pcd_data['cases_cumulative'].astype(int)

    # DECISION 4: retrospectively cap each cumulative value at the lowest value later confirmed for that healthzone
    pcd_data['cases_cumulative_corrected'] = (
        pcd_data.iloc[::-1]
                .groupby('healthzone')['cases_cumulative']
                .cummin()
                .iloc[::-1]
    )

    # Decision 5: compute new cases based on corrected cumulative cases
    pcd_data["cases_new"] = (
        pcd_data.groupby("healthzone")["cases_cumulative_corrected"]
        .diff()
        .fillna(pcd_data["cases_cumulative"])
    )    

    return pcd_data