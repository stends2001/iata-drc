import geopandas as gpd 
import pandas as pd 

from dataclasses import dataclass

from ..utils import PathManager
from ..utils.countries import countrycodes_dict

pm = PathManager()

@dataclass
class CountryShp:
    """Simple container for processed shape data."""
    name: str
    code: str
    
    shp: gpd.GeoDataFrame
    
    capital: gpd.GeoDataFrame
    label: gpd.GeoDataFrame
    airports: gpd.GeoDataFrame | None = None

    @classmethod
    def load(cls, name : str, 
             all_capitals : gpd.GeoDataFrame, 
             all_labels : gpd.GeoDataFrame, 
             all_airports : gpd.GeoDataFrame) -> "CountryShp":

        airport_sel = all_airports[all_airports['country'] == name].reset_index(drop = True)

        if len(airport_sel) == 0:
            airport_sel = None
        
        return CountryShp(
            name,
            countrycodes_dict[name],
            
            gpd.read_file(pm.data / 'processed' / 'shapedata' / name / f"{name}.shp"),
            all_capitals[all_capitals['country'] == name].reset_index(drop = True),  
            all_labels[all_labels['country'] == name].reset_index(drop = True),    
            airport_sel,                                 
        )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}({self.name})>"


def load_shapedata() -> dict[str, CountryShp]:
    shapedata = {}

    capitals    = gpd.read_file(pm.data / 'processed' / 'shapedata' / 'shared' / 'capitals.shp')
    labels      = gpd.read_file(pm.data / 'processed' / 'shapedata' / 'shared' / 'countryname_labels.shp')
    airports    = gpd.read_file(pm.data / 'processed' / 'shapedata' / 'shared' / 'airports.shp')        

    for countryname, countrycode in countrycodes_dict.items():
        shapedata[countryname] = CountryShp.load(countryname,
                                                 capitals,
                                                 labels,
                                                 airports)

    return shapedata