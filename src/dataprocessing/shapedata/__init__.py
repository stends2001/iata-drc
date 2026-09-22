from .shapedata import load_shapedata
from .capitals import load_capitals, preprocess_capitals
from ...utils.pathmanager import PathManager

def process_shapedata():

    pm = PathManager()
    raw_capitals = load_capitals(pm.data / 'raw' / 'shapedata' / 'country-capital-lat-long-population.csv')
    pcd_capitals = preprocess_capitals(raw_capitals)

    raw_shps, pcd_shps         = load_shapedata(pm.data / 'raw' / 'shapedata', pcd_capitals)
    return pcd_shps