import numpy as np
import pandas as pd
import plotly.graph_objects as go

from ....utils.countries import countries_by_continent, continent_colors
from ...utils import airport_colors

GREY_NODE, GREY_LINK = '#52514e', '#a3a29c'


def _rgba(h, a):
    h = h.lstrip('#'); return f'rgba({int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)},{a})'


def _col_y(sizes, pad):
    tot, avail, y, out = sum(sizes), 1 - pad * (len(sizes) - 1), 0.0, []
    for s in sizes:
        h = avail * s / tot; out.append(min(max(y + h / 2, 0.001), 0.999)); y += h + pad
    return out


def _top_or_other(s: pd.Series, keep, other: str) -> pd.Series:
    return s.where(s.isin(keep), other)


# ------------------------------------------------------------------------------------------------
# Figure 1a / 1b: domestic DRC trips, origin airport -> destination airport
# ------------------------------------------------------------------------------------------------
def _sankey_origin_destination(f: pd.DataFrame, value: str, top_k_origins: int, top_k_destinations: int,
                               always_show, label_fmt, hover: str, title: str, subtitle: str | None = None):
    """shared two-column Sankey: trip_origin_ap -> trip_destination_ap, widths = column `value`"""
    f = f[(f['trip_origin_ap'] != f['trip_destination_ap']) & (f[value] > 0)].copy()

    # top-k by volume, plus always_show airports so they never disappear into 'other'
    top_o = f.groupby('trip_origin_ap')[value].sum().nlargest(top_k_origins).index.union(list(always_show))
    top_d = f.groupby('trip_destination_ap')[value].sum().nlargest(top_k_destinations).index.union(list(always_show))
    f['origin'] = _top_or_other(f['trip_origin_ap'], top_o, 'other DRC airports')
    f['dest']   = _top_or_other(f['trip_destination_ap'], top_d, 'other DRC airports ')   # trailing space: separate node

    l0 = f.groupby(['origin', 'dest'])[value].sum()
    o_size, d_size = f.groupby('origin')[value].sum(), f.groupby('dest')[value].sum()

    def order(s, other):
        o = list(s.sort_values(ascending=False).index)
        return [x for x in o if x != other] + ([other] if other in o else [])
    origins, dests = order(o_size, 'other DRC airports'), order(d_size, 'other DRC airports ')

    keys   = [('o', o) for o in origins] + [('d', d) for d in dests]
    idx    = {k: i for i, k in enumerate(keys)}
    sizes  = [o_size[o] for o in origins] + [d_size[d] for d in dests]
    labels = [f'{k[1].strip()}  ({label_fmt(v)})' for k, v in zip(keys, sizes)]
    xs     = [0.001] * len(origins) + [0.999] * len(dests)
    ys     = _col_y([o_size[o] for o in origins], 0.03) + _col_y([d_size[d] for d in dests], 0.03)
    colors = [airport_colors.get(k[1].strip(), GREY_NODE) for k in keys]

    src, tgt, val, col = [], [], [], []
    for (o, d), v in l0.items():
        src.append(idx[('o', o)]); tgt.append(idx[('d', d)]); val.append(v)
        col.append(_rgba(airport_colors.get(o, GREY_LINK), 0.45))

    fig = go.Figure(go.Sankey(
        arrangement='fixed',
        node=dict(label=labels, x=xs, y=ys, color=colors, pad=8, thickness=16, line=dict(width=0)),
        link=dict(source=src, target=tgt, value=val, color=col, hovertemplate=hover),
    ))
    fig.update_layout(
        title=dict(text=f'<b>{title}</b><br><sup>{subtitle}</sup>', x=0.01, font=dict(size=16)),
        font=dict(size=12, color='#0b0b0b'), paper_bgcolor='#fcfcfb',
        height=560, margin=dict(l=20, r=20, t=80, b=20))
    return fig


def plot_sankey_drc_domestic_passengers(df: pd.DataFrame,
                                        start_date: str = '2026-04-01',
                                        end_date: str = '2026-08-01',
                                        top_k_origins: int = 5,
                                        top_k_destinations: int = 5,
                                        always_show: tuple = ('BUX', 'FKI', 'BNC', 'IRP')):
    """
    Domestic DRC trips: origin airport -> destination airport, widths = passengers (trips).

    please supply zone_in as df
    """
    f = df[(df['trip_origin_co'] == 'drc') & (df['trip_destination_co'] == 'drc') &
           (df['timestamp'] >= start_date) & (df['timestamp'] <= end_date)]
    f = f.groupby(['trip_origin_ap', 'trip_destination_ap'])['passengers'].sum().reset_index()
    return _sankey_origin_destination(
        f, 'passengers', top_k_origins, top_k_destinations, always_show,
        label_fmt=lambda v: f'{v:,.0f}',
        hover='%{source.label} → %{target.label}<br>%{value:,.0f} passengers<extra></extra>',
        title=f'Domestic trips within DRC, by destination airport  ·  '
              f'{pd.Timestamp(start_date):%b}–{pd.Timestamp(end_date):%b %Y}',
        subtitle='observed IATA trips starting and ending in DRC; labels = passengers; layovers ignored')


def plot_sankey_drc_domestic_risk(flights_dom_sum: pd.DataFrame,
                                  start_date: str = '2026-05-01',
                                  end_date: str = '2026-08-01',
                                  top_k_origins: int = 5,
                                  top_k_destinations: int = 5,
                                  always_show: tuple = ('BUX', 'FKI', 'BNC', 'IRP')):
    """
    Case-weighted domestic arrivals: origin airport -> destination airport,
    widths = passengers x catchment incidence at the origin (I_o/1e5 * T_o->h); destination totals = W_in.

    please supply flights_dom_sum (needs column 'weighted')
    """
    f = flights_dom_sum[(flights_dom_sum['timestamp'] >= start_date) & (flights_dom_sum['timestamp'] <= end_date)]
    f = f.groupby(['trip_origin_ap', 'trip_destination_ap'])['weighted'].sum().reset_index()
    tot = f['weighted'].sum()
    return _sankey_origin_destination(
        f, 'weighted', top_k_origins, top_k_destinations, always_show,
        label_fmt=lambda v: f'{v / tot:.1%}',
        hover='%{source.label} → %{target.label}<br>%{value:.3g} case-weighted passengers<extra></extra>',
        title=f'Case-weighted domestic trips within DRC')


# ------------------------------------------------------------------------------------------------
# Figure 2: propagated international risk, exit airport -> region -> country
# ------------------------------------------------------------------------------------------------
def propagated_intl_risk(intl_local: pd.DataFrame, intl_onward: pd.DataFrame, zone_out: pd.DataFrame,
                         start_date: str = '2026-05-01', end_date: str = '2026-08-01') -> pd.DataFrame:
    """
    Split each DRC airport's export index over destination countries.

      local  part: intl_local[h,t]  * T[h->d,t] / T_intl[h,t]      (exact: = I_h,t/1e5 * T[h->d,t])
      onward part: intl_onward[h,t] * T[h->d]   / T_intl[h]        (period destination mix of h; assumption)

    Returns tidy: exit, country, component, value (case-weighted passengers, summed over the period).
    """
    in_period = lambda c: (pd.Timestamp(c) >= pd.Timestamp(start_date)) & (pd.Timestamp(c) <= pd.Timestamp(end_date))
    cols = [c for c in intl_local.columns if in_period(c)]

    intl = zone_out[(zone_out['trip_origin_co'] == 'drc') & (zone_out['trip_destination_co'] != 'drc') &
                    (zone_out['timestamp'] >= start_date) & (zone_out['timestamp'] <= end_date)]
    T = intl.groupby(['trip_origin_ap', 'timestamp', 'trip_destination_co'])['passengers'].sum().rename('T').reset_index()

    # local: monthly destination mix
    T['mix_t'] = T['T'] / T.groupby(['trip_origin_ap', 'timestamp'])['T'].transform('sum')
    loc = intl_local[cols].stack().rename('R').rename_axis(['trip_origin_ap', 'timestamp']).reset_index()
    a = T.merge(loc, on=['trip_origin_ap', 'timestamp'], how='inner')
    a = (a.assign(value=a['R'] * a['mix_t'])
          .groupby(['trip_origin_ap', 'trip_destination_co'])['value'].sum().reset_index().assign(component='local'))

    # onward: period destination mix
    mix_p = T.groupby(['trip_origin_ap', 'trip_destination_co'])['T'].sum()
    mix_p = (mix_p / mix_p.groupby(level=0).transform('sum')).rename('mix').reset_index()
    onw = intl_onward[cols].sum(axis=1).rename('R').rename_axis('trip_origin_ap').reset_index()
    b = mix_p.merge(onw, on='trip_origin_ap', how='inner')
    b = b.assign(value=b['R'] * b['mix'], component='onward')[['trip_origin_ap', 'trip_destination_co', 'value', 'component']]

    out = pd.concat([a, b], ignore_index=True).rename(columns={'trip_origin_ap': 'exit', 'trip_destination_co': 'country'})
    return out[out['value'] > 0]


def plot_sankey_propagated_intl_risk(flows: pd.DataFrame,
                                     start_date: str = '2026-05-01',
                                     end_date: str = '2026-08-01',
                                     top_k_airports: int = 4,
                                     top_k_countries_per_region: int = 3):
    """Same layout as plot_sankey_drc_airport_to_countries, but widths = propagated export index (share of total)."""
    f = flows.copy()
    tot = f['value'].sum()
    top_ap = f.groupby('exit')['value'].sum().nlargest(top_k_airports).index
    f['origin']  = _top_or_other(f['exit'], top_ap, 'other DRC airports')
    f['region']  = f['country'].map(countries_by_continent).fillna('other/unknown')
    f['country'] = f['country'].str.replace('_', ' ').str.title()
    rank = f.groupby(['region', 'country'])['value'].sum().groupby(level=0, group_keys=False).rank(ascending=False)
    f = f.join(rank.rename('rank'), on=['region', 'country'])
    f['country'] = np.where(f['rank'] <= top_k_countries_per_region, f['country'], 'other ' + f['region'])

    l0 = f.groupby(['origin', 'region'])['value'].sum()
    l1 = f.groupby(['region', 'country'])['value'].sum()
    origins = list(f.groupby('origin')['value'].sum().sort_values(ascending=False).index)
    origins = [o for o in origins if o != 'other DRC airports'] + (['other DRC airports'] if 'other DRC airports' in origins else [])
    regs = [r for r in continent_colors if r in l1.index.get_level_values(0)]
    ctrs = [(r, c) for r in regs for c in l1[r].sort_values(ascending=False).index]
    o_size, r_size = f.groupby('origin')['value'].sum(), l1.groupby(level=0).sum()

    keys   = [('o', o) for o in origins] + [('r', r) for r in regs] + [('c', rc) for rc in ctrs]
    idx    = {k: i for i, k in enumerate(keys)}
    labels = origins + regs + [c for _, c in ctrs]
    sizes  = [o_size[o] for o in origins] + [r_size[r] for r in regs] + [l1[rc] for rc in ctrs]
    xs     = [0.001] * len(origins) + [0.42] * len(regs) + [0.999] * len(ctrs)
    ys     = _col_y([o_size[o] for o in origins], 0.03) + _col_y([r_size[r] for r in regs], 0.02) + \
             _col_y([l1[rc] for rc in ctrs], 0.006)
    colors = [airport_colors.get(o, GREY_NODE) for o in origins] + [continent_colors[r] for r in regs] + ['#c3c2b7'] * len(ctrs)

    src, tgt, val, col = [], [], [], []
    for (o, r), v in l0.items():
        src.append(idx[('o', o)]); tgt.append(idx[('r', r)]); val.append(v); col.append(_rgba(continent_colors[r], 0.35))
    for (r, c), v in l1.items():
        src.append(idx[('r', r)]); tgt.append(idx[('c', (r, c))]); val.append(v); col.append(_rgba(continent_colors[r], 0.45))

    fig = go.Figure(go.Sankey(
        arrangement='fixed',
        node=dict(label=[f'{l}  ({s / tot:.1%})' for l, s in zip(labels, sizes)], x=xs, y=ys, color=colors,
                  pad=6, thickness=16, line=dict(width=0)),
        link=dict(source=src, target=tgt, value=val, color=col,
                  hovertemplate='%{source.label} → %{target.label}<br>%{value:.3g} case-weighted passengers<extra></extra>'),
    ))
    fig.update_layout(
        title=dict(text=f'<b>Relative export index from DRC airports, by final destination</b>',
                   x=0.01, font=dict(size=16)),
        font=dict(size=12, color='#0b0b0b'), paper_bgcolor='#fcfcfb',
        height=max(620, 20 * len(ctrs)), margin=dict(l=20, r=20, t=80, b=20))
    return fig