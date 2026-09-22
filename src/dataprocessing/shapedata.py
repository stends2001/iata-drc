""" 
Here we get a dictionary ``countryshapes`` of processed shape files where each key is the name of that country
as listed in ``countries_background`` and ``countries_highlighted``. The values are instances of ``Countryshp``
with the attribute ``shp`` a gpd.GeoDataFrame with columns 'country', 'name', 'admin_level' and 'geometry'. 
When the country is a background country, the only value for 'admin_level' is 'adm0'. When it concerns a 
'highlighted' country, then values are 'adm0', 'adm1' or 'adm2'.
"""

import geopandas as gpd 
from tqdm import tqdm 
from pathlib import Path
from .shapedata_containers import Countryshp, Countryrawshp
from ..utils.countries import countries_background, countries_highglighted, countrycodes_dict

def load_shapedata(raw_path : Path,
                   capitals_geometry : gpd.GeoDataFrame
                   ) -> tuple[dict[str, Countryrawshp], dict[str, Countryshp]]:
    rawcountryshapes: dict[str, Countryrawshp] = {}
    countryshapes: dict[str, Countryshp]        = {}

    for countryname, countrycode in tqdm(countrycodes_dict.items()):
        path        = raw_path / countryname 
        file_base   = 'geoBoundaries-' + countrycode.upper()

        shp = Countryrawshp(
            countryname, 
            countrycode,
            gpd.read_file(path / (file_base + "-" + "ADM0.shp")),           
            gpd.read_file(path / (file_base + "-" + "ADM1.shp")) if countryname in countries_highglighted else None,
            gpd.read_file(path / (file_base + "-" + "ADM2.shp")) if countryname in countries_highglighted else None,                      
        )

        countryshapes[countryname] = shp.process(capitals_geometry[capitals_geometry['country'] == countryname])
        rawcountryshapes[countryname] = shp 

    return rawcountryshapes, countryshapes