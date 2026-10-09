import pandas as pd
import geopandas as gpd

from .utils import Mode
from .attractivity import get_airport_attractivity
from .catchment_incidence import get_catchment_incidence
from .distance import get_distance_matrix
from .huff import get_huff
from .propagate import propagate

from ..dataprocessing.airport_closures import apply_airport_closures, airports_closed_since
from ..utils.constants import crs_metres
# mode : air[ports, months]


from dataclasses import dataclass 

@dataclass
class HuffOutput:
    
    S : pd.DataFrame 
    D : pd.DataFrame 
    H : pd.DataFrame | dict[str, pd.DataFrame]
    I : pd.DataFrame 

    risk_dom : pd.DataFrame 
    risk_intl : pd.DataFrame
    intl_pax :  pd.DataFrame

    # context
    airports : list[str]
    closures : bool


def run_analysis(df_out : pd.DataFrame,
                 df_in : pd.DataFrame,
                 closures : bool,
                 mode : Mode,
                 airports : list[str],
                 drc_shape : gpd.GeoDataFrame,
                 airports_shape : gpd.GeoDataFrame,
                 months : list[str],
                 population_df : pd.DataFrame,
                 monthly_cases : pd.DataFrame
                 ) -> HuffOutput:
    """ 
    population_df = pcd_population
    
    """
    if closures:
        df_in = apply_airport_closures(df_in)
        df_out = apply_airport_closures(df_out)

    population = population_df.set_index('healthzone')['population'].astype(float)

    index_months = pd.date_range(
        start="2026-01-01",
        periods=9,
        freq="MS",
    )

    airports_shape = (airports_shape[airports_shape['code'].isin(airports)] # may also change to zone 1
                        .to_crs(crs_metres)[['code', 'geometry']]).rename(columns = {'code':'airport'}).reset_index(drop =True)

    S  = get_airport_attractivity(df_out, 
                                  airports, 
                                  mode, 
                                  months = months)

    D = get_distance_matrix(drc_shape[drc_shape['admin_level'] == 'healthzone'], 
                            airports_shape, 'euclidian-distance')

    H = get_huff(D, S, mode)

    I = get_catchment_incidence(H, population, monthly_cases, index_months)

    risk_dom, risk_intl, intl_pax  = propagate(df_out, df_in, airports, I, index_months)

    return HuffOutput(
                S, 
                D,
                H,
                I,
                risk_dom,
                risk_intl,
                intl_pax,
                airports,
                closures
                )