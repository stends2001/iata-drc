from .shapedata import load_shapedata, get_drc_harmfile
from .capitals import load_capitals, preprocess_capitals
from .iata_airports import load_airports_shapedata, process_airports_shapedata
from .drc_road_network import load_drc_road_network
from ...utils.pathmanager import PathManager

def process_shapedata(verbose : bool = False):

    pm = PathManager()
    raw_capitals = load_capitals(pm.data / 'raw' / 'shapedata' / 'country-capital-lat-long-population.csv')
    pcd_capitals = preprocess_capitals(raw_capitals)

    raw_shps, pcd_shps         = load_shapedata(pm.data / 'raw' / 'shapedata', pcd_capitals, verbose)
    return pcd_shps