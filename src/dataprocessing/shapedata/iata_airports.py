import geopandas as gpd 
from pathlib import Path

def load_airports_shapedata(rawpath : Path) -> gpd.GeoDataFrame:
    return gpd.read_file(rawpath / 'shapedata' / 'airports' / 'iata_airports.shp')