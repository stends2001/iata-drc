import geopandas as gpd 
from pathlib import Path 

def load_drc_road_network(rawpath : Path) -> gpd.GeoDataFrame:
    networks = gpd.read_file(rawpath / 'shapedata' /'drc_roads' / 'osm_rd_congo_main_roads_network.geojson')
    return networks