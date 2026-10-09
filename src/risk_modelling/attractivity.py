import pandas as pd

from .utils import Mode

def get_airport_attractivity(df: pd.DataFrame, airports : list[str], mode : Mode, months) -> pd.DataFrame:
   """
   Get airport attractivity, either static or a timeseries.

   Parameters
   -----------
   df: pd.DataFrame
      data on which to base attractivity; should be zone-out.
   mode : Literal['static', 'timeseries']
      whether to have airport attractivity static over time or timeseries.
   """
   out      = df[df['trip_origin_ap'].isin(airports)& (df['timestamp'].isin(months))]

   if mode == 'static':
      S_wide = out.groupby(['trip_origin_ap'])['passengers'].sum().reindex(fill_value=0)

      floor  = round(S_wide[S_wide > 0].median() * 0.05)
      S_wide = S_wide.where(S_wide == 0, S_wide.clip(lower=floor))
      airport_attractivity= S_wide.rename('attractivity').rename_axis(['airport']).reset_index()

   else: 
      S_wide = (out.pivot_table(index='trip_origin_ap', 
                              columns='timestamp', 
                              values='passengers',
                           aggfunc='sum', fill_value=0)
               .reindex(columns=months, fill_value=0))               # every month present, 0 where no trips

      floor  = round(S_wide[S_wide > 0].stack().median() * 0.05)
      S_wide = S_wide.where(S_wide == 0, S_wide.clip(lower=floor))

      airport_attractivity = (S_wide.stack().rename('attractivity').rename_axis(['airport', 'timestamp']).reset_index())
   return airport_attractivity