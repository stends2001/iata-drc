import pandas as pd 
import numpy as np

def by_airport(df : pd.DataFrame, 
               airports:list[str],
               months:list[str],
               value='passengers', 
               index='trip_origin_ap',
               ):

    """ 
    returns dataframe with
    - columns : timestamps
    - values : number of outbound passengers
    - index : airport
    """

    df_wide = (df.pivot_table(index=index, 
                              columns='timestamp', 
                              values=value, 
                              aggfunc='sum', 
                              fill_value=0)
                 .reindex(index=airports, columns=months, fill_value=0))
    
    return df_wide

def get_outgoing_flights(df : pd.DataFrame, airports) -> pd.DataFrame:
    dfc = df[df['trip_origin_ap'].isin(airports)]
    return dfc

def propagate_domestic_risk(df : pd.DataFrame, catchment_incidence : pd.DataFrame, airports, scaling_factor : float = 1e5):
    flights_dom     = df[(df['trip_origin_ap'].isin(airports)) & (df['trip_destination_ap'].isin(airports))]
    flights_dom_sum = flights_dom.groupby(['trip_origin_ap', 
                                           'trip_destination_ap', 
                                           'timestamp'])['passengers'].sum().reset_index()
    flights_dom_sum['r_origin'] = (catchment_incidence
                                   .stack()
                                   .reindex(list(zip(flights_dom_sum['trip_origin_ap'], 
                                                     flights_dom_sum['timestamp'])))
                                    .fillna(0).values)
    flights_dom_sum['r_origin'] = flights_dom_sum['r_origin'] / scaling_factor
    
    flights_dom_sum['weighted'] = flights_dom_sum['passengers'] * flights_dom_sum['r_origin']     

    return flights_dom_sum

def propate_international_risk(total_passengers_per_airport : pd.DataFrame, 
                               international_passengers_per_airport : pd.DataFrame,
                               international_share_per_airport : pd.DataFrame,
                               catchment_weighted_in : pd.DataFrame,
                               catchment_incidence : pd.DataFrame, 
                               scaling_factor : float = 1e5):
    
    risk_all_departures = (catchment_incidence / scaling_factor * total_passengers_per_airport).fillna(0)
    risk_all_departures = risk_all_departures.fillna(0)

    risk_intl_local     = (catchment_incidence) / scaling_factor * international_passengers_per_airport
    risk_intl_onward    = catchment_weighted_in.mul(international_share_per_airport, axis = 0)

    risk_intl_dep       = risk_intl_local + risk_intl_onward
    risk_intl_dep       = risk_intl_dep.fillna(0)
    return risk_intl_dep

def propagate(df1 : pd.DataFrame,
              df2 : pd.DataFrame,
              airports : list[str],
              catchment_incidence : pd.DataFrame,
              months):
    
    # df1: zone_out

    outgoing_flights    = get_outgoing_flights(df1, airports)
    passengers_per_airp = by_airport(outgoing_flights, airports, months)
    international_passengers_per_airp = by_airport(outgoing_flights[outgoing_flights['trip_destination_co'] != 'drc'], airports, months)
    international_share  = (international_passengers_per_airp.sum(axis=1) / passengers_per_airp.sum(axis=1).replace(0, np.nan)).fillna(0)   # from the data

    # 3. domestic flows between DRC airports (dataset 1 has trip_destination_ap)
    dom_prop  = propagate_domestic_risk(df2, catchment_incidence, airports)
    w_in      = by_airport(dom_prop, airports, months, value = 'weighted',  index ='trip_destination_ap')     # case-weighted domestic arrivals
    intl_risk = propate_international_risk(passengers_per_airp, international_passengers_per_airp, international_share, w_in, catchment_incidence)

    return w_in, intl_risk, international_passengers_per_airp 
