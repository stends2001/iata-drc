import geopandas as gpd 
import pandas as pd
from dataclasses import dataclass

@dataclass
class Countryshp:
    """Simple container for processed shape data."""
    name: str
    code: str
    shp: gpd.GeoDataFrame
    capital: gpd.GeoDataFrame

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}({self.name})>"

@dataclass
class Countryrawshp:
    """
    Simple container for raw shape data with possible resolutions of admin0-2.
    To get a container of processed data, use ``process()``.
    """    
    name: str
    code: str
    admin0: gpd.GeoDataFrame 
    admin1: gpd.GeoDataFrame | None
    admin2: gpd.GeoDataFrame | None

    def process(self, capital: gpd.GeoDataFrame) -> Countryshp:
        """
        Returns a processed shape data in form of ``Countryshp`` instance.
        This method orchestrates the following four subprocesses:
        - renaming of columns
        - selection of columns
        - make all string values lowercase
        - merge the shapes for all geographical resolutions (when available).
        """
        if self.admin1 is None or self.admin2 is None:
            gdf_merged = gpd.GeoDataFrame(
                self._lowercase(self._select_cols(self._rename_cols(self.admin0)))
                )

        else:
            gdf_merged = gpd.GeoDataFrame(
                pd.concat([
                    self._lowercase(self._select_cols(self._rename_cols(self.admin0))),
                    self._lowercase(self._select_cols(self._rename_cols(self.admin1))),
                    self._lowercase(self._select_cols(self._rename_cols(self.admin2)))
                ]))

        return Countryshp(
            self.name, 
            self.code, 
            gdf_merged, 
            capital[['city','geometry']].reset_index(drop = True)
            )
    
    def _rename_cols(self, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        columns_mapping = {
            'shapeName' : 'name',
            'shapeType' : 'admin_level',
            'shapeGroup': 'country'
        }
        return gdf.rename(columns = columns_mapping)

    def _select_cols(self, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        columns = ['country','name','admin_level','geometry']
        return gdf[columns]

    def _lowercase(self, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        gdf['country']      = gdf['country'].str.lower()
        gdf['name']         = gdf['name'].str.lower()
        gdf['admin_level']  = gdf['admin_level'].str.lower()
        return gdf
                
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}({self.name})>"