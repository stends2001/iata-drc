import pandas as pd
import geopandas as gpd

_double_mapping_population= {
        ("Nord-Ubangi", "Bili"): "bili (nord-ubangi)",
        ("Bas-Uele", "Bili"): "bili (bas-uele)",
        ("Tshopo", "Lubunga"): "lubunga (tshopo)",
        ("Kasaï-Central", "Lubunga"): "lubunga (kasaï-central)",
    }

def adjust_doubles_population_size(df : pd.DataFrame) -> pd.DataFrame:

    for (province, healthzone), replacement in _double_mapping_population.items():
        mask = (df["province"] == province) & (df["healthzone"] == healthzone)
        df.loc[mask, "healthzone"] = replacement    

    return df

_double_mapping_shapedata= {
        'r10719515': "bili (nord-ubangi)",
        'r10715430': "bili (bas-uele)",
        'r10741359': "lubunga (kasaï-central)",
        'r10749422': "lubunga (tshopo)",                        
    }

def adjust_double_shapedata(gdf : gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    for idv, healthzone in _double_mapping_shapedata.items():
        mask = (gdf["full_id"] == idv)
        gdf.loc[mask, "name"] = healthzone    

    return gdf
        