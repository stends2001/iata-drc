import pandas as pd 
from pathlib import Path 

mappings = {
    'Congo  Democratic Republic of' : 'drc',
    'Congo'                         : 'congo',
    'Uganda'                        : 'uganda',
    'South Sudan'                   : 'south sudan'
    }

def load_raw_iata(rawpath : Path, filename):
    """load raw iata data"""
    return pd.read_csv(rawpath / 'iata' / (filename + ".csv"))

def preprocess_iata_data(df : pd.DataFrame) -> pd.DataFrame:
    """
    preprocess iata data

    That is, adjust the columnsnames, timestamps and the countrynames.
    """

    df = df.dropna()

    df.rename(columns = {
        'Travel Month'              :   'month_year',
        'Trip Orig Desc'            :   'trip_origin_city',
        'Trip Dest Desc'            :   'trip_destination_city',
        'Trip Dest'                 :   'trip_destination_ap',
        'Trip Orig'                 :   'trip_origin_ap',
        'Trip Orig Country Desc'    :   'trip_origin_co',
        'Trip Dest Country Desc'    :   'trip_destination_co',
        'Seg Dest'                  :   'seg_destination_ap',
        'Seg Orig'                  :   'seg_origin_ap',
        'Seg Orig Country Desc'     :   'seg_origin_co',
        'Seg Dest Country Desc'     :   'seg_destination_co',
        'Pax Count'                 :   'passengers' 
    }, inplace = True)
    df['timestamp'] = pd.to_datetime(df["month_year"], format="%b %Y")    

    for column in ['trip_origin_co','trip_destination_co', 'seg_destination_co', 'seg_origin_co']:

        if column in df.columns.tolist(): 
            df[column]=df[column].replace(mappings)

    df = df.drop(columns = ['month_year'])
    return  df