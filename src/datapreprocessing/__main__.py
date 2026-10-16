from ..utils import PathManager
from .shapedata.capitals import raw_capitals, preprocess_capitals
from .utils import save_gdf

if __name__ == '__main__':
    pm = PathManager()
    
    raw_data = raw_capitals(pm.data / 'raw' / 'shapedata' / 'country-capital-lat-long-population.csv')
    pcd_data = preprocess_capitals(raw_data)
    
    save_gdf(pcd_data,
             pm.data / 'processed' / 'shapedata' / "shared" / "capitals.shp",
             )
