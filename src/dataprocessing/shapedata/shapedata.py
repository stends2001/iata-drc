""" 
Here we get a dictionary ``countryshapes`` of processed shape files where each key is the name of that country
as listed in ``countries_background`` and ``countries_highlighted``. The values are instances of ``Countryshp``
with the attribute ``shp`` a gpd.GeoDataFrame with columns 'country', 'name', 'admin_level' and 'geometry'. 
When the country is a background country, the only value for 'admin_level' is 'adm0'. When it concerns a 
'highlighted' country, then values are 'adm0', 'adm1' or 'adm2'.
"""

import geopandas as gpd 
import pandas as pd
from tqdm import tqdm 
from pathlib import Path
from ...utils.drc_mappings import mapping_pop
from .shapedata_containers import Countryshp, Countryrawshp
from ...utils.countries import countries_background, countries_highglighted, countrycodes_dict

def load_shapedata(raw_path : Path,
                   capitals_geometry : gpd.GeoDataFrame,
                   verbose : bool
                   ) -> tuple[dict[str, Countryrawshp], dict[str, Countryshp]]:
    rawcountryshapes: dict[str, Countryrawshp] = {}
    countryshapes: dict[str, Countryshp]        = {}

    if verbose:
        iterator = tqdm(countrycodes_dict.items())
    else:
        iterator = countrycodes_dict.items()

    for countryname, countrycode in iterator:
        path        = raw_path / countryname 
        file_base   = 'geoBoundaries-' + countrycode.upper()

        shp = Countryrawshp(
            countryname, 
            countrycode,
            gpd.read_file(path / (file_base + "-" + "ADM0.shp")),           
            gpd.read_file(path / (file_base + "-" + "ADM1.shp")) if countryname in countries_highglighted else None,
            gpd.read_file(path / (file_base + "-" + "ADM2.shp")) if countryname in countries_highglighted else None,       
            deeper = [load_drc_health_zones(path)] if countryname == 'drc' else None
        )

        countryshapes[countryname] = shp.process(capitals_geometry[capitals_geometry['country'] == countryname])
        rawcountryshapes[countryname] = shp 

    return rawcountryshapes, countryshapes

def load_drc_health_zones(path : Path) -> gpd.GeoDataFrame:
    drc_hz = gpd.read_file(path / 'osm_rdc_sante_zones_211212.gpkg')
    drc_hz = drc_hz[['name','geometry']]
    drc_hz['shapeGroup'] = 'cod'
    drc_hz['shapeType'] = 'healthzone'
    drc_hz.rename(columns = {'name' : 'shapeName'}, inplace = True)    
    return drc_hz

def get_drc_harmfile(raw_data_path : Path) -> pd.DataFrame:
    population_data                 = pd.read_excel(raw_data_path / 'drc-hpc-projection-population-2024.xlsx')
    population_data['healthzone']   = population_data['Zone de sante'].replace(mapping_pop)
    harmfile                        = population_data[['Province','Territoire','healthzone']].rename(columns = {'Province':'province','Territoire':'territoire'})
    for col in harmfile.columns.tolist():
        harmfile[col] = harmfile[col].str.lower()
    return harmfile
