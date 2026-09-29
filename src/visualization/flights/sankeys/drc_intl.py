# needs CONTINENT from the earlier cell
import numpy as np
import plotly.graph_objects as go
import pandas as pd

from ....utils.countries import countries_by_continent, continent_colors

def plot_sankey_drc_airport_to_countries(df : pd.DataFrame,
                                         start_date: str = '2026-04-01',
                                         end_date: str = '2026-08-01',
                                         top_k_airports : int = 4,
                                         top_k_countries_per_region : int = 3):
    """
    
    please supply zone_out at df
    """

    def rgba(h, a):
        h = h.lstrip('#'); return f'rgba({int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)},{a})'

    def col_y(sizes, pad):
        tot, avail, y, out = sum(sizes), 1 - pad * (len(sizes) - 1), 0.0, []
        for s in sizes:
            h = avail * s / tot; out.append(min(max(y + h / 2, 0.001), 0.999)); y += h + pad
        return out

    # filter on origin / destination
    df = df[(df['trip_origin_co'] == 'drc') & (df['trip_destination_co'] != 'drc')]
    
    # filter on time
    flights = df[(df['timestamp'] >= start_date) & (df['timestamp'] <= end_date)].copy()

    # find top k airports
    top_airports = flights.groupby('trip_origin_ap')['passengers'].sum().nlargest(top_k_airports).index

    # define origin column: if top k airport, then specifiy the airport, else 'other'
    flights['origin']  = flights['trip_origin_ap'].where(flights['trip_origin_ap'].isin(top_airports), 'other DRC airports')

    # define region column: if top k country in the region, then specifiy the country, else 'other'    
    flights['region']  = flights['trip_destination_co'].map(countries_by_continent).fillna('other')
    flights['country'] = flights['trip_destination_co'].str.replace('_', ' ').str.title()

    # rank the countries inside each region
    rank = flights.groupby(['region', 'country'])['passengers'].sum().groupby(level=0, group_keys=False).rank(ascending=False)

    # add ranks to flights data
    flights = flights.join(rank.rename('rank'), on=['region', 'country'])
    flights['country'] = np.where(flights['rank'] <= top_k_countries_per_region, flights['country'], 'other ' + flights['region'])

    # layer 0 : drc-airports -> region
    l0 = flights.groupby(['origin', 'region'])['passengers'].sum()

    # layer 1 : region -> country
    l1 = flights.groupby(['region', 'country'])['passengers'].sum()       # region  -> country

    # get lists of countries, airports and regions
    origins = list(flights.groupby('origin')['passengers'].sum().sort_values(ascending=False).index)
    origins = [o for o in origins if o != 'other DRC airports'] + (['other DRC airports'] if 'other DRC airports' in origins else [])
    regs    = [r for r in continent_colors if r in l1.index.get_level_values(0)]
    ctrs    = [(r, c) for r in regs for c in l1[r].sort_values(ascending=False).index]

    # get the sizes of the airports and regions
    o_size = flights.groupby('origin')['passengers'].sum()
    r_size = l1.groupby(level=0).sum()

    # get keys - indices - labels - sizes - colors and coordinates for labels
    keys   = [('o', o) for o in origins] + [('r', r) for r in regs] + [('c', rc) for rc in ctrs]
    idx    = {k: i for i, k in enumerate(keys)}
    labels = origins + regs + [c for _, c in ctrs]
    sizes  = [o_size[o] for o in origins] + [r_size[r] for r in regs] + [l1[rc] for rc in ctrs]
    xs     = [0.001] * len(origins) + [0.42] * len(regs) + [0.999] * len(ctrs)
    ys     = col_y([o_size[o] for o in origins], 0.03) + col_y([r_size[r] for r in regs], 0.02) + \
            col_y([l1[rc] for rc in ctrs], 0.006)
    colors = ['#52514e'] * len(origins) + [continent_colors[r] for r in regs] + ['#c3c2b7'] * len(ctrs)

    src, tgt, val, col = [], [], [], []
    for (o, r), v in l0.items():
        src.append(idx[('o', o)]); tgt.append(idx[('r', r)]); val.append(v); col.append(rgba(continent_colors[r], 0.35))
    for (r, c), v in l1.items():
        src.append(idx[('r', r)]); tgt.append(idx[('c', (r, c))]); val.append(v); col.append(rgba(continent_colors[r], 0.45))

    fig = go.Figure(go.Sankey(
        arrangement='fixed',
        node=dict(label=[f'{l}  ({n:,.0f})' for l, n in zip(labels, sizes)], x=xs, y=ys, color=colors,
                pad=6, thickness=16, line=dict(width=0)),
        link=dict(source=src, target=tgt, value=val, color=col,
                hovertemplate='%{source.label} → %{target.label}<br>%{value:,.0f} passengers<extra></extra>'),
    ))
    fig.update_layout(
        title=dict(text=f'<b>International trips from DRC airports, by final destination</b>  ·  '
                        f'{pd.Timestamp(start_date):%b}–{pd.Timestamp(end_date):%b %Y}'
                        '<br><sup>observed IATA trips starting at each airport; domestic trips excluded; layovers ignored</sup>',
                x=0.01, font=dict(size=16)),
        font=dict(size=12, color='#0b0b0b'), paper_bgcolor='#fcfcfb',
        height=max(620, 20 * len(ctrs)), margin=dict(l=20, r=20, t=80, b=20))
    return fig

    # # the numbers behind it: each airport's destination mix (share of its international trips)
    # mix = flights.pivot_table(index='origin', columns='region', values='passengers', aggfunc='sum', fill_value=0)
    # print((mix.div(mix.sum(axis=1), axis=0) * 100).round(1).loc[origins])