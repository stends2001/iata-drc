import geopandas as gpd 
import pandas as pd 
from dataclasses import dataclass 
import numpy as np

from ...utils import fix_winding

from ....utils.region_mappings import uga_adm2_drc_namesakes, drc_provinces

@dataclass
class CountryPcdshp:
    """Simple container for processed shape data."""
    name: str
    code: str
    
    shp: gpd.GeoDataFrame 
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}({self.name})>"

@dataclass
class CountryRawShp:
    """
    Container for raw shape data with possible resolutions of admin0-2.
    To get a container of processed data, use ``process()``.

    More resolution is allowed, deeper than admin2, on the condition that it is fed in as list of gdfs.
    Further, required columns are ``'shapeName'``, ``'shapeType'`` and ``'shapeGroup'``.
    """    
    name: str
    code: str

    admin0: gpd.GeoDataFrame 
    admin1: gpd.GeoDataFrame | None
    admin2: gpd.GeoDataFrame | None

    deeper: list[gpd.GeoDataFrame] | None = None # drc : healthzones

    def process(self) -> CountryPcdshp:
        """
        Returns a processed shape data in form of ``Countryshp`` instance.
        This method orchestrates the following four subprocesses:
        - renaming of columns
        - selection of columns
        - make all string values lowercase
        - merge the shapes for all geographical resolutions (when available).
        """

        match (self.admin0, self.admin1, self.admin2, self.deeper):

            # when only adm0 supplied 
            case gpd.GeoDataFrame(), None, None, None:
                main_gdf = gpd.GeoDataFrame(
                    self._lowercase(self._select_cols(self._rename_cols(self.admin0)))
                    )

            # when only adm0 - adm2 supplied
            case gpd.GeoDataFrame(), gpd.GeoDataFrame(), gpd.GeoDataFrame(), None:
                main_gdf = gpd.GeoDataFrame(
                    pd.concat([self._lowercase(self._select_cols(self._rename_cols(gdf))) 
                            for gdf in [self.admin0, self.admin1, self.admin2]])
                )

            case gpd.GeoDataFrame(), gpd.GeoDataFrame(), gpd.GeoDataFrame(), list():
                main_gdf = gpd.GeoDataFrame(
                    pd.concat([self._lowercase(self._select_cols(self._rename_cols(gdf))) 
                            for gdf in [self.admin0, self.admin1, self.admin2] + self.deeper])
                )

            case _:
                raise ValueError('Invalid combination of arguments supplied to CountryRawShp')

        main_gdf = self._process_country_specs(main_gdf)
        main_gdf, dropped = self._clip_to_national_boundary(main_gdf)

        if len(dropped) > 0:
            raise ValueError(f'careful with {self.name}. rows were dropped : {dropped}')

        return CountryPcdshp(
            self.name, 
            self.code, 
            main_gdf, 
            )
    
    def _rename_cols(self, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        columns_mapping = {
            'shapeName' : 'name',
            'shapeType' : 'admlvl',
            'shapeGroup': 'country'
        }
        return gdf.rename(columns = columns_mapping)

    def _select_cols(self, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        columns = ['country','name','admlvl','geometry']
        return gdf[columns]

    def _lowercase(self, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        gdf['country']      = gdf['country'].str.lower()
        gdf['name']         = gdf['name'].str.lower()
        gdf['admlvl']       = gdf['admlvl'].str.lower()
        return gdf

    def _process_country_specs(self, gdf : gpd.GeoDataFrame) -> gpd.GeoDataFrame:

        match self.name:

            case 'drc':
                mapping_dict = drc_provinces
                gdf['name'] = gdf['name'].replace(mapping_dict)      

                # was a specific issue with orientation of polygons
                gdf.geometry = gdf.geometry.apply(fix_winding)
            case 'uganda':
                # couple of regions in DRC and Uganda have the same name.
                # we adjust those in Uganda.
                mapping_dict = uga_adm2_drc_namesakes
                gdf['name'] = gdf['name'].replace(mapping_dict)                  

            case _:
                pass

        return gdf

    def _clip_to_national_boundary(self, gdf: gpd.GeoDataFrame) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
        """Returns (clipped, dropped); dropped has original rows + 'drop_reason' ('outside' / 'touches_only')."""
        empty = gdf.iloc[0:0].assign(drop_reason=pd.Series(dtype=str))
        if self.admin1 is None or self.admin2 is None:
            return gdf, empty

        gdf     = gdf.assign(_row=range(len(gdf)))
        is_adm0 = gdf['admlvl'] == 'adm0'
        assert is_adm0.sum() == 1, f'expected exactly one adm0 row, got {is_adm0.sum()}'
        mask    = gdf.loc[is_adm0].geometry.make_valid().iloc[0]

        lower   = gdf.loc[~is_adm0].copy()
        lower   = lower.set_geometry(lower.geometry.make_valid())
        clipped = gpd.clip(lower, mask, keep_geom_type=True)
        clipped = clipped[clipped.geometry.notna() & ~clipped.geometry.is_empty]
        clipped = clipped.dissolve(by='_row', as_index=False, aggfunc='first')[lower.columns]        

        dropped = lower[~lower['_row'].isin(clipped['_row'])].copy()
        dropped['drop_reason'] = np.where(dropped.geometry.intersects(mask), 'touches_only', 'outside')

        out = pd.concat([gdf.loc[is_adm0], clipped]).sort_values('_row').drop(columns='_row')
        return (gpd.GeoDataFrame(out, geometry='geometry', crs=gdf.crs),
                dropped.drop(columns='_row'))

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}({self.name})>"