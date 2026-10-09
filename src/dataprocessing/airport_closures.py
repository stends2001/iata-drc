import pandas as pd 

def load_airport_closures() -> pd.DataFrame:

    events = {
        '2026-05-23': 'Bunia airport - All flights suspended',
        '2026-06-02': 'Bunia airport - Airport Reopened',
        '2026-06-08': 'Bunia airport - Commercial flights suspended',
    }

    airport_closures = (
        pd.Series(events, name='Event')
        .rename_axis('Date')
        .reset_index()
    )

    airport_closures['Date'] = pd.to_datetime(airport_closures['Date'])
    return airport_closures

def apply_airport_closures(df: pd.DataFrame, closure_dict : dict[str, str]) -> pd.DataFrame:
    """Remove trips from (and, where known, to) airports in the months they were closed."""
    df = df.copy()
    for airport, since in closure_dict.items():
        touches = df['trip_origin_ap'] == airport

        if 'trip_destination_ap' in df.columns:
            touches |= df['trip_destination_ap'] == airport

        df = df[~(touches & (df['timestamp'] >= since))]

    return df