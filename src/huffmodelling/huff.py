import pandas as pd
from .utils import Mode

def get_huff(
    distance_matrix : pd.DataFrame, 
    attractivity    : pd.DataFrame,        
    mode            : Mode,

    ALPHA       : float = 0.5,          # attractiveness exponent: 0 = size ignored, 1 = proportional to size
    BETA        : float = 2.0,          # distance friction: 2 is the classic gravity value
    D_MIN_KM    : float = 10,           # floor on distance (zones containing an airport would otherwise blow up)
    MAX_KM      : float = 400,          # airports further away are not an option
    D_HOME      : float | None  = None, # 'not flying' = as attractive as a median-size airport at this distance; None = classic Huff        
    ):

    """
    Get Huff proportions: those that indicate which airport people in which region take.
    Note that when mode is 'timeseries', i.e. when huff should have a temporal axis, attractivity
    is expected to have one too, and therefore have a column 'timestamp'

    Parameters
    ----------
    distance_matrix : 
    attractivity :
    mode :

    ALPHA:
    BETA: 
    D_MIN_KM
    MAX_KM
    D_HOME
    """

    def _single_timestamp_huff(D: pd.DataFrame, S: pd.DataFrame):
            S = S.set_index('airport')['attractivity']  
            S = S.reindex(D.columns).astype(float).fillna(0)                          # missing airport = not available  

            D_eff = D.clip(lower=D_MIN_KM)
            upper = (D_eff ** -BETA).mul(S ** ALPHA, axis=1).where(D <= MAX_KM, 0) 
            U0    = 0.0 if D_HOME is None else (S[S > 0].median() ** ALPHA) * D_HOME ** -BETA

            huff = upper.div(upper.sum(axis=1) + U0, axis=0).fillna(0)  
            return huff

    match mode:
        
        case 'static' :
            H = _single_timestamp_huff(distance_matrix, attractivity)
            

        case 'timeseries':
            if not 'timestamp' in attractivity.columns:
                raise ValueError('expected column "timestam" in attractivity for mode "timeseries".')       

            H = {t: _single_timestamp_huff(distance_matrix, a.drop(columns='timestamp'),)
                    for t, a in attractivity.groupby('timestamp')}               

    return  H
