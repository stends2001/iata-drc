import numpy as np
import pandas as pd
import geopandas as gpd
from matplotlib.axes import Axes
from matplotlib.lines import Line2D
from shapely.geometry import box
from typing import Literal
from ...dataprocessing.shapedata.shapedata_containers import Countryshp

from .utils import geomap_args, box_coordinates
from ...utils.constants import crs_degrees, crs_metres

CAPITAL_COLOR = '#8c510a'                                               # brown
CASE_STYLE    = dict(color='red', edgecolor='black', linewidth=0.5)     # case dots
HZ_STYLE      = dict(facecolor='none', edgecolor='#52514e', linewidth=0.4)
PROVINCES_LABELLED = ['bas-uele', 'haut-uele', 'ituri', 'nord-kivu', 'tshopo', 'sud-kivu']


# ------------------------------------------------------------------------------------------------
# legend helpers
# ------------------------------------------------------------------------------------------------
def _bin_labels(bins):
    """Labels for integer bins with right=False: [a, b)."""
    labels = []
    for a, b in zip(bins[:-1], bins[1:]):
        a = int(a)
        if np.isinf(b):
            labels.append(f'≥{a}')
        elif b - a == 1:
            labels.append(f'{a}')
        else:
            labels.append(f'{a}–{int(b) - 1}')
    return labels


def _marker_handle(style: dict, label: str, **override) -> Line2D:
    """Legend marker from a geopandas-style kwargs dict (markersize = area in points²)."""
    s = {**style, **override}
    face = s.get('facecolor', s.get('color', 'grey'))
    return Line2D([], [], linestyle='', label=label,
                  marker=s.get('marker', 'o'),
                  markerfacecolor=face,
                  markeredgecolor=s.get('edgecolor', face),
                  markeredgewidth=s.get('linewidth', 0.5),
                  markersize=np.sqrt(s.get('markersize', 36)))


def _line_handle(style: dict, label: str) -> Line2D:
    """Legend line from a geopandas-style polygon kwargs dict (boundary = edgecolor)."""
    return Line2D([], [], label=label,
                  color=style.get('edgecolor', style.get('color', 'grey')),
                  linewidth=style.get('linewidth', style.get('lw', 0.8)),
                  linestyle=style.get('linestyle', style.get('ls', '-')))


def _add_legend(ax: Axes, **kwargs):
    """Add a legend without replacing legends that are already on the axes."""
    ax.add_artist(ax.legend(**kwargs))


# ------------------------------------------------------------------------------------------------
# 1. background: DRC + surrounding countries + labels + capitals
# ------------------------------------------------------------------------------------------------
def plot_geography_background(ax: Axes,
                              shapedata: dict[str, Countryshp],
                              legend: bool = True,):
    """
    DRC with provinces, surrounding countries in grey, country and province labels,
    capitals in brown. Sets the map extent to box_coordinates['drc'].
    """
    x_min, x_max = box_coordinates['drc']['x']
    y_min, y_max = box_coordinates['drc']['y']
    map_box      = box(x_min, y_min, x_max, y_max)

    ax.set_facecolor(**geomap_args['sea'])
    capital_style = {**geomap_args['capital'], 'color': CAPITAL_COLOR}

    for country_name, country_shape in shapedata.items():
        gdf = country_shape.shp

        # country shape: DRC with provinces, others national outline only
        if country_name == 'drc':
            for admin_lvl in ['adm0', 'adm1']:
                sub_section = gdf[gdf['admin_level'] == admin_lvl]
                sub_section.plot(ax=ax, **geomap_args[admin_lvl])

                if admin_lvl == 'adm1':
                    for _, row in sub_section[sub_section['name'].isin(PROVINCES_LABELLED)].iterrows():
                        p = row.geometry.representative_point()
                        ax.text(p.x, p.y, row['name'].replace("-", " ").capitalize(),
                                ha="center", va="center", fontsize=9, zorder=4)
        else:
            gdf[gdf['admin_level'] == 'adm0'].plot(ax=ax, **geomap_args['background_countries'])

        # country name, placed inside the visible part of the country
        for _, row in gdf[gdf['admin_level'] == 'adm0'].iterrows():
            clipped_geometry = row.geometry.intersection(map_box)
            if not clipped_geometry.is_empty:
                p = clipped_geometry.representative_point()
                ax.text(p.x, p.y, country_name.replace("_", " ").upper(),
                        ha="center", va="center", fontweight="bold", zorder=4,
                        fontsize=11 if country_name == 'drc' else 8)

        # capital
        country_shape.capital.plot(ax=ax, zorder=3, **capital_style)

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)

    if legend:
        _add_legend(ax, handles=[_marker_handle(capital_style, 'Capital', facecolor=CAPITAL_COLOR),
                                 _line_handle(geomap_args['adm1'], 'Province boundary')],
                    loc='lower right', fontsize=8)


# ------------------------------------------------------------------------------------------------
# 2. overlay: case dots + outlines of the health zones with a dot
# ------------------------------------------------------------------------------------------------
def add_casedots_and_healthzones(ax: Axes,
                                 shapedata: dict[str, Countryshp],
                                 casedata: pd.DataFrame,
                                 rel_differences : pd.DataFrame | None,
                                 rel_differences_dates : list[str] | None,
                                 bins: list = [0, 1, 10, 50, 150, float('inf')],
                                 sizes: list = [10, 20, 40, 50, 75],
                                 legend: bool = True,
                                 crs: Literal['metres','degrees'] = 'degrees'):
    """
    Cumulative cases per health zone as dots (size by class), with the outlines of those
    health zones. Draw on top of plot_geography_background (or any DRC map).
    """
    xlim, ylim = ax.get_xlim(), ax.get_ylim()           # keep the extent set by the background

    if rel_differences is not None:

        if rel_differences_dates is None:
            raise ValueError('when supplying a df for rel_differences please also supply the date labels')

        casedata = pd.merge(casedata.rename(columns = {'cases_cumulative_corrected' : f'cases_cumulative_{rel_differences_dates[0]}'}), 
                            rel_differences.rename(columns = {'cases_cumulative_corrected' : f'cases_cumulative_{rel_differences_dates[1]}'}), 
                            on = ['healthzone']).fillna(0)

        casedata['delta'] = casedata[f'cases_cumulative_{rel_differences_dates[0]}'] - casedata[f'cases_cumulative_{rel_differences_dates[1]}']
        casedata = casedata[casedata['delta'] > 0]
        
    
    casedata['markersize'] = pd.cut(
            casedata['cases_cumulative_corrected'] if rel_differences is None else casedata['delta'],
            bins=bins,
            labels=sizes,
            right=False
        ).astype(int)

    hz_all = shapedata['drc'].shp[shapedata['drc'].shp['admin_level'] == 'healthzone']
    gdf = gpd.GeoDataFrame(pd.merge(casedata, hz_all, left_on='healthzone', right_on='name'))

    # outlines: above country/province fills, below the dots
    hz_all[hz_all['name'].isin(gdf['name'])].plot(ax=ax, zorder=2, **HZ_STYLE)

    # dots
    gdf['geometry'] = gdf['geometry'].representative_point()
    newcrs = crs_metres if crs == 'metres' else crs_degrees
    gdf = gdf.to_crs(newcrs)
    gdf.plot(ax=ax, markersize=gdf['markersize'], zorder=3, **CASE_STYLE)

    ax.set_xlim(xlim)
    ax.set_ylim(ylim)

    if legend:
        handles = [_marker_handle(CASE_STYLE, lab, markersize=s) for s, lab in zip(sizes, _bin_labels(bins))]
        handles.append(_line_handle(HZ_STYLE, 'Health zone with cases'))
        _add_legend(ax, handles=handles, 
                    title='Cumulative cases\nper health zone' if rel_differences_dates is None else f'New cases between\n{rel_differences_dates[0]} - {rel_differences_dates[1]}',
                    loc='lower left', fontsize=8, title_fontsize=9, labelspacing=1.0, borderpad=0.8)