from shapely import make_valid
import pandas as pd 
import geopandas as gpd 
import numpy as np

from ..utils.constants import crs_metres

def get_distance_matrix(
    health_zones_shp: gpd.GeoDataFrame, 
    airport_shp : gpd.GeoDataFrame        
    ) -> pd.DataFrame:
    health_zones_shp = health_zones_shp.rename(columns = {'name':'healthzone'}).to_crs(crs_metres)
    health_zones_shp = health_zones_shp.sort_values(by = 'healthzone')
    region_centroids =  health_zones_shp.set_index('healthzone').geometry.centroid
    airports         = airport_shp.set_index('code')
    distance_mtx     = pd.DataFrame({
                        a: region_centroids.distance(g) / 1000 for a, g in airports.geometry.items()
                        })    # km, zone x airport
    return distance_mtx

def get_huff(
    distance_matrix : pd.DataFrame, 
    attractivity : pd.DataFrame ,        
    ALPHA : float    = 0.5,     # attractiveness exponent: 0 = size ignored, 1 = proportional to size
    BETA : float     = 2.0,     # distance friction: 2 is the classic gravity value
    D_MIN_KM : float = 10,     # floor on distance (zones containing an airport would otherwise blow up)
    MAX_KM : float  = 400,     # airports further away are not an option
    D_HOME : float | None  = None,     # 'not flying' = as attractive as a median-size airport at this distance; None = classic Huff        
    ):
    S = attractivity.set_index('airport')['attractivity']    # your 
    S = S.reindex(distance_matrix.columns).astype(float)

    D_eff = distance_matrix.clip(lower=D_MIN_KM)
    upper = (D_eff ** -BETA).mul(S ** ALPHA, axis=1).where(distance_matrix <= MAX_KM, 0)
    U0    = 0.0 if D_HOME is None else (S.median() ** ALPHA) * D_HOME ** -BETA
    return upper.div(upper.sum(axis=1) + U0, axis=0).fillna(0)  
    
def get_catchment_incidence(huff: pd.DataFrame,
                            population: pd.Series,     # healthzone -> population
                            cases: pd.DataFrame        # healthzone x month
                            ) -> pd.DataFrame:
    N = population.reindex(huff.index)
    if N.isna().any():
        print('zones without population (set to 0):', list(N.index[N.isna()]))
    N = N.fillna(0).astype(float)
    C = cases.reindex(huff.index).fillna(0)
    catch_pop   = huff.T.dot(N)
    catch_cases = huff.T.dot(C)
    I = catch_cases.div(catch_pop.replace(0, np.nan), axis=0).fillna(0) * 1e5
    return I

def get_catchment_areas(huff : pd.DataFrame, 
                         healthzones_shp : gpd.GeoDataFrame):

    if healthzones_shp.crs != crs_metres:
        healthzones_shp = healthzones_shp.to_crs(crs_metres)


    flies = huff.sum(axis=1)    

    hz_catchments = healthzones_shp.set_index('healthzone')[['geometry']].assign(
        airport=huff.idxmax(axis=1).where(flies > 0),
        p_main=huff.max(axis=1) / flies.replace(0, np.nan)
        )           # how dominant that airport is (0-1)
    
    g = hz_catchments.dropna(subset=['airport'])[['airport', 'geometry']].copy()
    bad = ~g.is_valid 
    g.loc[bad, 'geometry'] = make_valid(g.loc[bad, 'geometry'].values)   # repair only the broken ones, in one go

    catchment_areas = g.dissolve(by='airport').reset_index()    
    return catchment_areas, hz_catchments