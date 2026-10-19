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

def is_international(df : pd.DataFrame) -> pd.Series:
    """International = destination country differs from the trip's OWN origin country
    (so EBB -> Kampala is domestic for Uganda, EBB -> Nairobi international)."""
    return df['trip_destination_co'] != df['trip_origin_co']

def propagate_domestic_risk(df : pd.DataFrame, catchment_incidence : pd.DataFrame, airports, scaling_factor : float = 1e5):
    """
    Case-weighted domestic trips between airports in `airports`.
    Only trips within one country (cross-border trips are already counted as international at
    their origin; counting them here as well would double count) and only between different airports.
    """
    flights_dom     = df[(df['trip_origin_ap'].isin(airports)) & (df['trip_destination_ap'].isin(airports))
                         & (df['trip_origin_ap'] != df['trip_destination_ap'])]
    if {'trip_origin_co', 'trip_destination_co'} <= set(df.columns):
        flights_dom = flights_dom[~is_international(flights_dom)]
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

def international_risk_components(international_passengers_per_airport : pd.DataFrame,
                                  international_share_per_airport : pd.Series,
                                  catchment_weighted_in : pd.DataFrame,
                                  catchment_incidence : pd.DataFrame,
                                  scaling_factor : float = 1e5) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Export index split in its two parts (airport x month):
      local  = I_h,t / 1e5 * T^intl_h,t     trips that START in h's catchment (through-tickets included)
      onward = s_h * W_h,t                  case-weighted domestic arrivals continuing abroad on a new ticket
                                            (ASSUMPTION: they continue like other passengers departing h)
    """
    risk_intl_local  = (catchment_incidence / scaling_factor * international_passengers_per_airport).fillna(0)
    risk_intl_onward = catchment_weighted_in.mul(international_share_per_airport, axis = 0).fillna(0)
    return risk_intl_local, risk_intl_onward

def propagate_international_risk(total_passengers_per_airport : pd.DataFrame,
                                 international_passengers_per_airport : pd.DataFrame,
                                 international_share_per_airport : pd.DataFrame,
                                 catchment_weighted_in : pd.DataFrame,
                                 catchment_incidence : pd.DataFrame,
                                 scaling_factor : float = 1e5):
    local, onward = international_risk_components(international_passengers_per_airport,
                                                  international_share_per_airport,
                                                  catchment_weighted_in, catchment_incidence, scaling_factor)
    return (local + onward).fillna(0)

propate_international_risk = propagate_international_risk     # old (misspelled) name, kept for existing code

def propagate_split(df1 : pd.DataFrame,
                    df2 : pd.DataFrame,
                    airports : list[str],
                    catchment_incidence : pd.DataFrame,
                    months) -> dict[str, pd.DataFrame | pd.Series]:
    """
    Same computation as `propagate`, but returns every intermediate (dict), incl. the local and onward
    parts of the export index separately.
    df1 : zone_out ; df2 : zone_in
    """
    outgoing_flights    = get_outgoing_flights(df1, airports)
    passengers_per_airp = by_airport(outgoing_flights, airports, months)
    international_passengers_per_airp = by_airport(outgoing_flights[is_international(outgoing_flights)], airports, months)
    international_share  = (international_passengers_per_airp.sum(axis=1) / passengers_per_airp.sum(axis=1).replace(0, np.nan)).fillna(0)   # from the data

    # domestic flows between airports in the list (dataset 2 has trip_destination_ap)
    dom_prop  = propagate_domestic_risk(df2, catchment_incidence, airports)
    w_in      = by_airport(dom_prop, airports, months, value = 'weighted',  index ='trip_destination_ap')     # case-weighted domestic arrivals
    local, onward = international_risk_components(international_passengers_per_airp, international_share, w_in, catchment_incidence)

    return dict(w_in=w_in, intl_local=local, intl_onward=onward, intl_risk=(local + onward),
                intl_pax=international_passengers_per_airp, intl_share=international_share,
                dom_flows=dom_prop)

def propagate(df1 : pd.DataFrame,
              df2 : pd.DataFrame,
              airports : list[str],
              catchment_incidence : pd.DataFrame,
              months):
    """Unchanged interface: returns (w_in, intl_risk, intl_pax)."""
    p = propagate_split(df1, df2, airports, catchment_incidence, months)
    return p['w_in'], p['intl_risk'], p['intl_pax']
