import geopandas as gpd 
from pathlib import Path
from shapely.geometry import Point

def load_airports_shapedata(rawpath : Path) -> gpd.GeoDataFrame:
    return gpd.read_file(rawpath / 'shapedata' / 'airports' / 'iata_airports.shp')

def process_airports_shapedata(gdf : gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    # ref for coordinates: https://ourairports.com/airports/FZMB
    mask = gdf["code"].eq("RUE")

    gdf.loc[mask, "city"] = "Butembo"
    gdf.loc[mask, "geometry"] = Point(29.312992, 0.117142)

    return gdf