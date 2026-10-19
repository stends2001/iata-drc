from pathlib import Path
import geopandas as gpd
from tqdm import tqdm 

from ....utils.countries import countries_zone1, countrycodes_dict
from .datacontainers import CountryRawShp

def load_raw_shapedata(raw_path : Path) -> tuple[dict[str, CountryRawShp]]:
    
    rawcountryshapes: dict[str, CountryRawShp]  = {}

    iterator = tqdm(countrycodes_dict.items())

    for countryname, countrycode in iterator:
        path        = raw_path / countryname 
        file_base   = 'geoBoundaries-' + countrycode.upper()

        adm0 = gpd.read_file(path / (file_base + "-" + "ADM0.shp"))

        match countryname:

            case 'uganda':
                adm1    = gpd.read_file(path / (file_base + "-" + "ADM1.shp"))                             
                adm2    = _load_uga_adm2(path / 'uga_admin2.shp', False)
                deeper  = None

            case 'drc' :
                adm1    = gpd.read_file(path / (file_base + "-" + "ADM1.shp"))                             
                adm2    = gpd.read_file(path / (file_base + "-" + "ADM2.shp"))         
                deeper  = [_load_drc_health_zones(path / 'osm_rdc_sante_zones_211212.gpkg')]

            case v if v in countries_zone1:
                adm1    = gpd.read_file(path / (file_base + "-" + "ADM1.shp"))                
                adm2    = gpd.read_file(path / (file_base + "-" + "ADM2.shp"))
                deeper  = None

            case _:
                adm1    = None
                adm2    = None
                deeper  = None

        shp = CountryRawShp(
            countryname, 
            countrycode,
            adm0,
            adm1, 
            adm2,
            deeper
        )

        rawcountryshapes[countryname] = shp 

    return rawcountryshapes

def _load_drc_health_zones(path : Path) -> gpd.GeoDataFrame:
    drc_hz = gpd.read_file(path)
    drc_hz = drc_hz[drc_hz['name'] != 'Mai Ndombe I'].reset_index(drop = True)


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


    drc_hz = adjust_double_shapedata(drc_hz)

    drc_hz = drc_hz[['name','geometry']]
    drc_hz['shapeGroup'] = 'cod'
    drc_hz['shapeType'] = 'healthzone'
    drc_hz.rename(columns = {'name' : 'shapeName'}, inplace = True)    
    return drc_hz

def _load_uga_adm2(path: Path, pcode : bool) -> gpd.GeoDataFrame:
    """  
    Uganda adm2 shapedata from the OTHER source is not right! We took a different source with has a different makeup of their data, here we transform that.
    """
    admin2 = gpd.read_file(path)

    # these regions exist in both Uganda and DRC. in DRC we keep their names, here we transform them.  
    
    admin2 = admin2.rename(columns = {
        'adm2_name' : 'shapeName',
        'geometry' : 'geometry'
    })
    admin2['shapeType'] = 'adm2'
    admin2['shapeGroup'] = 'UGA'

    cols = ['shapeName', 'shapeType',  'shapeGroup', 'geometry'] 
    if pcode: 
        cols = cols + ['adm2_pcode']

    admin2['shapeName'] = admin2['shapeName'].str.lower()
    
    return admin2[cols]