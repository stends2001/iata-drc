import geopandas as gpd
import pandas as pd

def get_harmfile(gdf : gpd.GeoDataFrame, level_dict: dict[str, str] = {} ) -> pd.DataFrame:    
    """
    Based on shapefile, returns a harmonization file
    Please put 'name' : ... in the level_dict, relating to the name of the finest units
    (district for Uganda, healthzone for DRC).
    """
    result = gdf.copy()
    levels = sorted(gdf["admlvl"].dropna().unique())

    for lvl in levels:
        lower = gdf[gdf["admlvl"] == lvl]

        for upper_lvl in levels:
            if upper_lvl >= lvl:
                continue

            upper = gdf.loc[
                gdf["admlvl"] == upper_lvl,
                ["name", "geometry"]
            ].copy()

            col = f"{upper_lvl}"
            upper = upper.rename(columns={"name": col})

            # Use a point inside each lower-level polygon
            lower_points = lower[["geometry"]].copy()
            lower_points["geometry"] = lower.geometry.representative_point()

            joined = gpd.sjoin(
                lower_points,
                upper[[col, "geometry"]],
                how="left",
                predicate="within"
            )

            result.loc[lower.index, col] = (
                joined.groupby(level=0)[col].first().reindex(lower.index)
            )
    cols = list(gdf["admlvl"].dropna().unique()[:-1])
    cols.append('name')
    result = result[cols].dropna().reset_index(drop = True)

    if len(level_dict) == 0:
        return result

    elif len(level_dict) != len(levels):
        raise ValueError(f'found {len(levels)} levels, input name is {len(level_dict)}')


    return result.rename(columns = level_dict)