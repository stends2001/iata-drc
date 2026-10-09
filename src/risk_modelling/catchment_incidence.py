import pandas as pd
import numpy as np
def get_catchment_incidence(huff : pd.DataFrame | dict[pd.Timestamp, pd.DataFrame],
          pop : pd.Series,
          cases : pd.DataFrame,
          index_months : list[str] | None = None,
          scaling_factor : float = 1e5) -> pd.DataFrame:
    """
    Catchment incidence I_jt = sum_i P_ij(t) C_it / sum_i P_ij(t) N_i * scaling_factor.

    huff  : zone x airport matrix (static) or {timestamp: matrix} (timeseries)
    pop   : population per health zone
    cases : health zone x month (new cases per month)
    Returns airport x month in both modes.
    """
    cases = cases.copy()
    cases.columns = pd.to_datetime(cases.columns)

    def _incidence(H: pd.DataFrame, C: pd.DataFrame | pd.Series):
        N   = pop.reindex(H.index).fillna(0)
        C   = C.reindex(H.index).fillna(0)
        num = H.T.dot(C)                          # airport (x month): sum_i P_ij C_i
        den = H.T.dot(N)                          # airport: sum_i P_ij N_i
        return num.div(den.replace(0, np.nan), axis=0).fillna(0) * scaling_factor

    missing_pop = pop.index[pop.isna()]
    if len(missing_pop):
        print('zones without population (set to 0):', list(missing_pop))

    if isinstance(huff, pd.DataFrame):            # static: one H for all months
        out = _incidence(huff, cases)

    else: 
        out = {}                                      # timeseries: month-specific H
        for t, H in huff.items():
            t = pd.Timestamp(t)
            C = cases[t] if t in cases.columns else pd.Series(0.0, index=H.index)
            out[t] = _incidence(H, C)
    
    if index_months is None:
        return pd.DataFrame(out)

    else:
        return pd.DataFrame(out).reindex(columns=index_months, fill_value=0)