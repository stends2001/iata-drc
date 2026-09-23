import geopandas as gpd 
import pandas as pd

from ..utils.constants import crs_degrees, crs_metres

def process_populationdenstiy_data(shapedata : gpd.GeoDataFrame, 
                                   populationdata : pd.DataFrame):
    """ 
    Return a geo dataframe with population_size, population_density and geometry per health zone.
    """
    healthzones_shape = shapedata[shapedata['admin_level'] == 'healthzone']

    pop_gdf = gpd.GeoDataFrame(
        pd.merge(healthzones_shape, 
                 populationdata, 
                 left_on = 'name', right_on = 'healthzone')
                 )
    
    pop_gdf["geometry"] = pop_gdf.geometry.make_valid()
    pop_gdf = pop_gdf.to_crs(crs_metres)
    pop_gdf["area_km2"] = pop_gdf.geometry.area / 1e6

    pop_gdf = pop_gdf.to_crs(crs_degrees)
    pop_gdf['population_density'] = pop_gdf['population'] / pop_gdf['area_km2']
    pop_gdf = pop_gdf[['healthzone','population','population_density','geometry']]
    return pop_gdf