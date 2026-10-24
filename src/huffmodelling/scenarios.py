"""
Run and compare scenarios of the Huff export model in one place.

    from src.huffmodelling.scenarios import BaseInputs, default_scenarios, run_scenarios

    base = BaseInputs(df_out=zone_out, df_in=zone_in, shapedata=shp, months=months,
                      population_df=pcd_population, monthly_cases=monthly_cases,
                      airport_colors=airport_colormapping)
    outputs, summary, captured = run_scenarios(default_scenarios(), base)

`summary`  : long table, one row per scenario x airport x month: local, onward, total export index,
             and the airport's share of the month's total.
`captured` : share of each month's cases that falls in some airport catchment (cases beyond MAX_KM,
             or behind a closed border, drop out -- compare scenarios only together with this).
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace

import numpy as np
import pandas as pd

from .run import run_analysis, HuffOutput, select_units
from .borders import BorderPolicy, to_country_code
from .utils import Mode
from .distance import DistanceMode


@dataclass
class Scenario:
    name: str
    countries: list[str] | None = None               # keys of shapedata to include; None = all
    closures: bool = True                             # airport closures as in airport_closures.py
    border_policy: BorderPolicy | None = None         # None = no border effect
    mode: Mode = 'timeseries'
    distance_mode: DistanceMode = 'great-circle'
    huff_kwargs: dict = field(default_factory=dict)   # ALPHA, BETA, D_MIN_KM, MAX_KM, D_HOME


@dataclass
class BaseInputs:
    df_out: pd.DataFrame
    df_in: pd.DataFrame
    shapedata: dict
    months: list
    population_df: pd.DataFrame
    monthly_cases: pd.DataFrame
    airport_colors: dict
    index_months: list | None = None
    distance_matrix: pd.DataFrame | None = None       # precomputed (e.g. road / travel time); overrides distance_mode


# --- standard scenario sets ---------------------------------------------------------------------
def default_scenarios(rho: float = 1.0) -> list[Scenario]:
    """S0-S4 from the paper plan. rho = share of would-be cross-border travellers that crosses."""
    return [
        Scenario('S0_drc_noclosures',    countries=['drc'], closures=False),
        Scenario('S1_drc_closures',      countries=['drc'], closures=True),
        Scenario('S2_uga_open',          countries=['drc', 'uganda'], closures=True,
                 border_policy=BorderPolicy.crossing(rho)),
        Scenario('S3_uga_reported',      countries=['drc', 'uganda'], closures=True,
                 border_policy=BorderPolicy.reported(rho)),
        Scenario('S4_uga_borderclosed',  countries=['drc', 'uganda'], closures=True,
                 border_policy=BorderPolicy.closed()),
    ]


RHOS = (1.0, 0.3, 0.1, 0.03, 0.01, 0.003, 0.001, 0.0003, 0.0001, 0.0)


def rho_sweep(template: Scenario, rhos=RHOS, with_reported_closures: bool = True) -> list[Scenario]:
    """Same scenario for a range of crossing shares rho (1 = open ... 0 = closed)."""
    out = []
    for r in rhos:
        pol = BorderPolicy.reported(r) if with_reported_closures else BorderPolicy.crossing(r)
        out.append(replace(template, name=f'{template.name}_rho{r:g}', border_policy=pol))
    return out


def border_sweep(template: Scenario, extra_kms=(0, 50, 100, 200, 400),
                 with_reported_closures: bool = True) -> list[Scenario]:
    """Secondary: distance cost in the Huff choice instead of a crossing share."""
    out = []
    for km in extra_kms:
        pol = BorderPolicy.penalty(km)
        if with_reported_closures:
            pol.closures, pol.name = dict(BorderPolicy.reported().closures), f'reported_{km:g}km'
        out.append(replace(template, name=f'{template.name}_border{km:g}km', border_policy=pol))
    return out


def huff_grid(template: Scenario, ALPHA=(0.25, 0.5, 1.0), BETA=(1.5, 2.0, 3.0),
              MAX_KM=(300, 400, 600)) -> list[Scenario]:
    """Sensitivity grid over the Huff parameters (27 runs with the defaults)."""
    out = []
    for a in ALPHA:
        for b in BETA:
            for m in MAX_KM:
                kw = {**template.huff_kwargs, 'ALPHA': a, 'BETA': b, 'MAX_KM': m}
                out.append(replace(template, name=f'{template.name}_a{a:g}_b{b:g}_max{m:g}', huff_kwargs=kw))
    return out


# --- running ------------------------------------------------------------------------------------
def run_scenario(sc: Scenario, base: BaseInputs) -> HuffOutput:
    shapedata = base.shapedata if sc.countries is None else {k: base.shapedata[k] for k in sc.countries}
    return run_analysis(base.df_out, base.df_in, sc.closures, sc.mode, shapedata, base.months,
                        base.population_df, base.monthly_cases, base.airport_colors,
                        index_months=base.index_months, distance_mode=sc.distance_mode,
                        distance_matrix=base.distance_matrix, border_policy=sc.border_policy,
                        **sc.huff_kwargs)


def _H_at(out: HuffOutput, t):
    """Huff matrix for month t (None if there is none for that month)."""
    if not isinstance(out.H, dict):
        return out.H
    return out.H.get(pd.Timestamp(t))


def cases_captured(out: HuffOutput, monthly_cases: pd.DataFrame) -> pd.Series:
    """Share of each month's cases that is assigned to any airport (row sums of H < 1 lose cases)."""
    cases = monthly_cases.copy()
    cases.columns = pd.to_datetime(cases.columns)
    months = out.I.columns
    vals = {}
    for t in months:
        H = _H_at(out, t)
        if H is None or t not in cases.columns:
            vals[t] = np.nan
            continue
        C = cases[t].reindex(H.index).fillna(0)
        vals[t] = (H.sum(axis=1) * C).sum() / C.sum() if C.sum() > 0 else np.nan
    return pd.Series(vals, name='cases_captured')


def crossborder_fraction(out: HuffOutput, monthly_cases: pd.DataFrame) -> pd.DataFrame:
    """airport x month: share of the cases in the airport's catchment that live in ANOTHER country
    (those travellers reach the airport overland across a border -> invisible to ticket data)."""
    cases = monthly_cases.copy()
    cases.columns = pd.to_datetime(cases.columns)
    uc = to_country_code(out.unitshapes.drop_duplicates('unit').set_index('unit')['country'])
    ac = to_country_code(out.airportshapes.drop_duplicates('airport').set_index('airport')['country'])
    res = {}
    for t in out.I.columns:
        H = _H_at(out, t)
        if H is None:
            continue
        if t not in cases.columns:
            res[t] = pd.Series(0.0, index=H.columns)
            continue
        C = cases[t].reindex(H.index).fillna(0).to_numpy()[:, None]
        cross = uc.reindex(H.index).to_numpy()[:, None] != ac.reindex(H.columns).to_numpy()[None, :]
        num_all = (H.to_numpy() * C).sum(axis=0)
        num_x = (H.to_numpy() * C * cross).sum(axis=0)
        res[t] = pd.Series(np.divide(num_x, num_all, out=np.zeros_like(num_x), where=num_all > 0), index=H.columns)
    return pd.DataFrame(res).fillna(0)


def summarise(out: HuffOutput, name: str, monthly_cases: pd.DataFrame | None = None) -> pd.DataFrame:
    """Long table: scenario x airport x month with the export index split into
         local_same   : through-tickets from the airport's own-country catchment (visible to ticket data)
         local_cross  : catchment residents who crossed a border by road first (invisible)
         onward       : domestic arrivals continuing abroad on a new ticket (invisible)
    plus totals and the airport's share of the month's total."""
    loc = out.risk_intl_local.stack().rename('local')
    onw = out.risk_intl_onward.stack().rename('onward')
    df = pd.concat([loc, onw], axis=1).fillna(0)
    df.index.names = ['airport', 'month']
    df = df.reset_index()
    if monthly_cases is not None:
        xf = crossborder_fraction(out, monthly_cases).stack()
        xf.index.names = ['airport', 'month']
        df = df.merge(xf.rename('xfrac').reset_index(), on=['airport', 'month'], how='left').fillna({'xfrac': 0})
    else:
        df['xfrac'] = 0.0
    df['local_cross'] = df['local'] * df['xfrac']
    df['local_same'] = df['local'] - df['local_cross']
    df = df.drop(columns='xfrac')
    df['total'] = df['local'] + df['onward']
    month_total = df.groupby('month')['total'].transform('sum')
    df['share_of_month'] = np.where(month_total > 0, df['total'] / month_total, np.nan)
    ap_country = out.airportshapes.drop_duplicates('airport').set_index('airport')['country']
    df['airport_country'] = df['airport'].map(ap_country)
    df.insert(0, 'scenario', name)
    return df


def implied_crossborder_travellers(out: HuffOutput, population_df: pd.DataFrame) -> pd.DataFrame:
    """airport x month: international departures that the model attributes to residents of ANOTHER
    country (who must have crossed a border first): T_intl_j * sum_cross H_ij N_i / sum_i H_ij N_i.
    Compare with real cross-border numbers to judge which rho is plausible."""
    N = population_df.set_index('unit')['population'].astype(float)
    uc = to_country_code(out.unitshapes.drop_duplicates('unit').set_index('unit')['country'])
    ac = to_country_code(out.airportshapes.drop_duplicates('airport').set_index('airport')['country'])
    res = {}
    for t in out.intl_pax.columns:
        H = _H_at(out, t)
        if H is None:
            continue
        n = N.reindex(H.index).fillna(0).to_numpy()[:, None]
        cross = uc.reindex(H.index).to_numpy()[:, None] != ac.reindex(H.columns).to_numpy()[None, :]
        w_all = (H.to_numpy() * n).sum(axis=0)
        w_x = (H.to_numpy() * n * cross).sum(axis=0)
        frac = np.divide(w_x, w_all, out=np.zeros_like(w_x), where=w_all > 0)
        res[t] = pd.Series(frac, index=H.columns) * out.intl_pax[t].reindex(H.columns).fillna(0)
    return pd.DataFrame(res)


def rho_table(outputs: dict, summary: pd.DataFrame, population_df: pd.DataFrame,
              airports=('EBB', 'FIH'), months=None) -> pd.DataFrame:
    """One row per rho-sweep scenario: export index per airport, EBB/FIH ratio, and the implied number
    of cross-border travellers per month flying out of the cross-border airports."""
    rows = []
    sweep = [n for n in outputs if '_rho' in n]
    for name in sweep:
        s = summary[summary['scenario'] == name]
        if months is not None:
            s = s[s['month'].isin(pd.to_datetime(months))]
        tot = s.groupby('airport')['total'].sum()
        imp = implied_crossborder_travellers(outputs[name], population_df)
        if months is not None:
            imp = imp.reindex(columns=pd.to_datetime(months))
        row = dict(scenario=name, rho=float(name.split('_rho')[-1]))
        for a in airports:
            row[f'index_{a}'] = tot.get(a, 0.0)
        row['ratio_EBB_FIH'] = row['index_EBB'] / row['index_FIH'] if row.get('index_FIH') else np.nan
        row['crossborder_travellers_per_month'] = imp.sum(axis=0).replace(0, np.nan).mean()
        rows.append(row)
    return pd.DataFrame(rows).sort_values('rho', ascending=False).reset_index(drop=True)


def run_scenarios(scenarios: list[Scenario], base: BaseInputs, verbose: bool = True):
    outputs, summaries, captured = {}, [], []
    for sc in scenarios:
        if verbose:
            print(f'running {sc.name} ...')
        out = run_scenario(sc, base)
        outputs[sc.name] = out
        summaries.append(summarise(out, sc.name, base.monthly_cases))
        captured.append(cases_captured(out, base.monthly_cases).rename(sc.name))
    summary = pd.concat(summaries, ignore_index=True)
    captured = pd.concat(captured, axis=1).T
    return outputs, summary, captured


# --- quick views --------------------------------------------------------------------------------
def gateway_shares(summary: pd.DataFrame, months=None, by: str = 'airport') -> pd.DataFrame:
    """Share of the total export index per scenario, over the chosen months (by airport or country)."""
    s = summary if months is None else summary[summary['month'].isin(pd.to_datetime(months))]
    tot = s.groupby(['scenario', by])['total'].sum()
    return (tot / tot.groupby(level=0).transform('sum')).unstack(by).fillna(0)


def invisible_share(summary: pd.DataFrame, months=None) -> pd.DataFrame:
    """Part of the export index that through-ticket data cannot see, split by route:
       onward (separate ticket via a hub) and local_cross (overland across a border first)."""
    s = summary if months is None else summary[summary['month'].isin(pd.to_datetime(months))]
    g = s.groupby('scenario')[['local_same', 'local_cross', 'onward', 'total']].sum()
    out = pd.DataFrame({'via_hub_separate_ticket': g['onward'] / g['total'],
                        'via_border_overland': g['local_cross'] / g['total']})
    out['invisible_total'] = out.sum(axis=1)
    return out


# --- entry point: python -m src.huffmodelling.scenarios (from the repo root) --------------------
def load_base_inputs() -> BaseInputs:
    """Load the processed data the same way for every scenario run."""
    from ..dataloading import (load_shapedata, load_iata_data, load_casedata,
                               load_population_drc, load_population_uga)
    from ..utils.sim_utils import months, airport_colormapping

    shapedata = load_shapedata()
    zone_in, zone_out = load_iata_data()                      # NB: returns (zone_in, zone_out)

    population = pd.concat([
        load_population_drc().rename(columns={'healthzone': 'unit'}),
        load_population_uga().rename(columns={'district': 'unit'}),
    ], ignore_index=True)[['unit', 'population']]

    cases = load_casedata()                                   # healthzone, timestamp, cases_new, ...
    monthly_cases = (cases.assign(month=cases['timestamp'].dt.to_period('M').dt.to_timestamp())
                          .pivot_table(index='healthzone', columns='month', values='cases_new',
                                       aggfunc='sum', fill_value=0))

    return BaseInputs(df_out=zone_out, df_in=zone_in, shapedata=shapedata, months=list(months),
                      population_df=population, monthly_cases=monthly_cases,
                      airport_colors=airport_colormapping, index_months=months)


def check_population(base: BaseInputs, countries=None) -> pd.DataFrame:
    """Units in the shapes that have no (or zero) population. Missing units silently get population 0 in
    the incidence step, which breaks the catchments (e.g. a Ugandan catchment of DRC residents only)."""
    shp = base.shapedata if countries is None else {k: base.shapedata[k] for k in countries}
    units = pd.concat([select_units(cs.shp)[['country', 'name']] for cs in shp.values()],
                      ignore_index=True).rename(columns={'name': 'unit'})
    for name, cs in shp.items():
        if len(select_units(cs.shp)) == 0:
            print(f"WARNING: no analysis units for '{name}' (admlvl values: {sorted(cs.shp['admlvl'].unique())}); "
                  f"set its level in run.UNIT_LEVELS")
    pop = base.population_df.drop_duplicates('unit').set_index('unit')['population']
    units['population'] = units['unit'].map(pop)
    bad = units[units['population'].isna() | (units['population'] <= 0)]
    summary = units.assign(missing=units['population'].isna() | (units['population'] <= 0)) \
                   .groupby('country')['missing'].agg(['sum', 'count']).rename(columns={'sum': 'missing', 'count': 'units'})
    print('units without population, per country:\n', summary)
    if len(bad):
        print('examples:', bad.groupby('country')['unit'].apply(lambda u: list(u)[:8]).to_dict())
        unused = sorted(set(pop.index) - set(units['unit']))
        print('population names not matching any unit (first 15):', unused[:15])
    return bad


def main(rho: float = 1.0, sweep: bool = True):
    from ..utils import PathManager

    base = load_base_inputs()
    bad = check_population(base, countries=['drc', 'uganda'])
    if len(bad):
        print(f'\nWARNING: {len(bad)} units have no population; results with Uganda are not reliable until fixed.\n')
    scenarios = default_scenarios(rho)
    if sweep:
        scenarios += rho_sweep(Scenario('sweep', countries=['drc', 'uganda'], closures=True))

    outputs, summary, captured = run_scenarios(scenarios, base)

    outdir = PathManager().data / 'results' / 'scenarios'
    outdir.mkdir(parents=True, exist_ok=True)
    summary.to_csv(outdir / 'summary.csv', index=False)
    captured.to_csv(outdir / 'cases_captured.csv')
    gateway_shares(summary).to_csv(outdir / 'gateway_shares.csv')
    invisible_share(summary).to_csv(outdir / 'invisible_share.csv')
    rt = rho_table(outputs, summary, base.population_df)
    rt.to_csv(outdir / 'rho_table.csv', index=False)

    pd.set_option('display.width', 200)
    print('\ngateway shares (whole period):\n', gateway_shares(summary).round(3))
    print('\ninvisible share:\n', invisible_share(summary).round(3))
    print('\ncases captured:\n', captured.round(3))
    print('\nrho sweep (whole period; crossborder_travellers = implied DRC residents flying out of Ugandan airports per month):\n',
          rt.round(4))
    print(f'\nresults written to {outdir}')
    return outputs, summary, captured


if __name__ == '__main__':
    main()