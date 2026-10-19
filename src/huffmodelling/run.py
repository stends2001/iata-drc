import pandas as pd
import geopandas as gpd

from .utils import Mode
from .attractivity import get_airport_attractivity
from .incidence import get_catchment_incidence
from .distance import get_distance_matrix, DistanceMode
from .huff import get_huff
from .propagate import propagate_split

from .airport_closures import apply_airport_closures, airports_closed_since
from ..utils.constants import crs_metres

from ..dataloading.shapedata import CountryShp

from dataclasses import dataclass, field

@dataclass
class HuffOutput:

    S : pd.DataFrame
    D : pd.DataFrame
    H : pd.DataFrame | dict[str, pd.DataFrame]
    I : pd.DataFrame

    risk_dom  : pd.DataFrame             # W: case-weighted domestic arrivals (airport x month)
    risk_intl : pd.DataFrame             # export index R = local + onward (airport x month)
    intl_pax  :  pd.DataFrame

    # context
    unitshapes  : gpd.GeoDataFrame
    globalshapes    : gpd.GeoDataFrame
    airportshapes   : gpd.GeoDataFrame
    closures        : bool
    airport_colors  : dict[str, str]

    # added: parts of the export index and run settings
    risk_intl_local  : pd.DataFrame | None = None     # I/1e5 * international trips starting at the airport
    risk_intl_onward : pd.DataFrame | None = None     # s_h * W_h (separate tickets via the airport)
    intl_share       : pd.Series | None = None        # s_h
    mode             : str | None = None
    distance_mode    : str | None = None
    closures_dict    : dict = field(default_factory=dict)
    huff_kwargs      : dict = field(default_factory=dict)


def run_analysis(df_out : pd.DataFrame,
                 df_in : pd.DataFrame,
                 closures : bool,
                 mode : Mode,
                 shapedata : dict[str, CountryShp],
                 months : list[str],
                 population_df : pd.DataFrame,
                 monthly_cases : pd.DataFrame,
                 airport_colors : dict[str, str],                 
                 index_months = None,
                 distance_mode : DistanceMode = 'euclidian-distance',
                 distance_matrix : pd.DataFrame | None = None,
                 **huff_kwargs,
                 ) -> HuffOutput:
    """
    population_df = pcd_population

    New (optional) arguments, defaults reproduce the previous behaviour:
      index_months    : months to compute incidence / risk for (default Jan-Sep 2026, as before)
      distance_mode   : 'euclidian-distance' (default, as before) | 'great-circle' | 'travel-time'
      friction_path   : friction GeoTIFF, needed for 'travel-time'
      distance_matrix : precomputed zone x airport matrix (skips get_distance_matrix; handy for
                        travel time, which takes a while to compute)
      **huff_kwargs   : passed to get_huff (ALPHA, BETA, D_MIN_KM, MAX_KM, D_HOME).
                        NB with travel time, D_MIN_KM and MAX_KM are in HOURS.
    """
    if closures:
        df_in = apply_airport_closures(df_in)
        df_out = apply_airport_closures(df_out)

    population = population_df.set_index('unit')['population'].astype(float)

    if index_months is None:
        index_months = pd.date_range(
            start="2026-01-01",
            periods=9,
            freq="MS",
        )
    index_months = pd.DatetimeIndex(index_months)

    airports_shp = []
    countries_shp= []
    for country_name, country_shape in shapedata.items():
        
        if country_shape.airports is not None:
            airports_shp.append(country_shape.airports)

        countries_shp.append(country_shape.shp)

    airports_shp = pd.concat(airports_shp).to_crs(crs_metres)
    airport_list = list(airports_shp['airport'].unique())
    countries_shp= pd.concat(countries_shp).to_crs(crs_metres)    

    unit_shapes = (countries_shp[countries_shp['admlvl'].isin(['district','healthzone'])]
                     .replace({"district" : 'unit', 'healthzone': 'unit'})
                     .rename(columns = {'name':'unit'})
                    )

    S  = get_airport_attractivity(df_out,
                                  airport_list,
                                  mode,
                                  months = months)

    if distance_matrix is None:
        D = get_distance_matrix(unit_shapes,
                                airports_shp, 
                                distance_mode)
    else:
        D = distance_matrix.reindex(columns=airports_shp['airport'])

    H = get_huff(D, S, mode, **huff_kwargs)

    I = get_catchment_incidence(H, population, monthly_cases, index_months)

    p = propagate_split(df_out, df_in, airport_list, I, index_months)

    return HuffOutput(
                S,
                D,
                H,
                I,
                p['w_in'],
                p['intl_risk'],
                p['intl_pax'],
                unit_shapes,
                countries_shp,
                airports_shp,
                closures,
                airport_colors,                
                risk_intl_local  = p['intl_local'],
                risk_intl_onward = p['intl_onward'],
                intl_share       = p['intl_share'],
                mode             = mode,
                distance_mode    = 'precomputed' if distance_matrix is not None else distance_mode,
                closures_dict    = dict(airports_closed_since) if closures else {},
                huff_kwargs      = huff_kwargs,
                )
