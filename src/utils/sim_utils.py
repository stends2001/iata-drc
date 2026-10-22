import pandas as pd 

months = pd.date_range(
    start="2026-01-01",
    periods=9,
    freq="MS",
)

airport_colormapping = {
    'FIH' : '#2a78d6',
    'GOM' : '#1b9e77',
    'FKI' : '#d95f02',
    'IRP' : '#4a3aa7',
    'BNC' : '#e7298a',
    'BUX' : '#008300',
    'FBM' : '#a6761d',
    'RUE' : "#4daba3",
    'EBB' : 'black',
    'JUB' : '#7570b3',
    'KXO' : '#e6ab02',
    'KHX' : '#66a61e'
}