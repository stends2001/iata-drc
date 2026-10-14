import geopandas as gpd
from ...utils.drc_mappings import uganda_namesakes_drc
from ...utils import PathManager

def get_adm2_uganda_shp(pcode : bool) -> gpd.GeoDataFrame:
    path_manager = PathManager()
    admin2 = gpd.read_file(path_manager.data / 'raw' / 'shapedata' / 'uganda' / 'uga_admin2.shp')
    admin2 = admin2.rename(columns = {
        'adm2_name' : 'shapeName',
        'geometry' : 'geometry'
    })
    admin2['shapeType'] = 'adm2'
    admin2['shapeGroup'] = 'UGA'

    cols = ['shapeName', 'shapeType',  'shapeGroup', 'geometry'] 
    if pcode: 
        cols = cols + ['adm2_pcode']

    admin2['shapeName'] = admin2['shapeName'].str.lower().replace(uganda_namesakes_drc)
    
    return admin2[cols]