"""
Border crossings for the Huff catchments: the border step of `run_analysis`.

Main parameter: rho, the share of travellers that actually crosses the border.

  1. Huff with the border open    -> H_open : unit i's flyers split over all airports in reach
  2. Huff with the border closed  -> H_none : the same, own-country airports only
  3. Of the flyers that H_open sends across a border, a share rho crosses; the other (1 - rho)
     use their own country's airports, split as in H_none:

        H = H_open(own country) + rho * H_open(across border) + (1 - rho) * c_i * H_none
            with c_i = share of unit i's flyers that H_open sends across a border

  rho = 1 -> border open (same as no border policy); rho = 0 -> border closed.
  A reported closure sets rho = 0 for that border in the months it counts as closed.

Reading rho: "of the eastern-DRC travellers for whom Entebbe is the nearest/biggest option,
a share rho crosses into Uganda to fly". The export index at a cross-border airport scales
roughly with rho, so the key output is the rho at which Entebbe and Kinshasa are equal, plus the
number of cross-border travellers that each rho implies (scenarios.implied_crossborder_travellers).

Optional, secondary: extra_km / factor make cross-border airports count as further away in the
Huff choice itself (D' = factor * D + extra_km). MAX_KM is always applied to the physical distance.

    from src.huffmodelling.run import run_analysis
    from src.huffmodelling.borders import BorderPolicy
    out = run_analysis(zone_out, zone_in, True, 'timeseries', shp, months, pcd_population,
                       monthly_cases, airport_colors, border_policy=BorderPolicy.reported(extra_km=100))
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from ..utils.countries import countrycodes_dict
from .huff import get_huff

# --- reported border closures (country pairs as ISO3 codes, as in the unit shapes) ----------------
# Best available dates (news / Logcluster; see claude/airport_status_2025_2026.md). Check before publishing.
BORDER_CLOSURES: dict[frozenset, list[tuple[str, str | None]]] = {
    # Uganda closed the border to passenger transport (and suspended DRC flights) ~21-23 May 2026;
    # Uganda's outbreak declared over 28 Jul; nonstop traffic back in the August IATA data.
    frozenset({'cod', 'uga'}): [('2026-05-21', '2026-07-31')],
    # Goma-Gisenyi crossing closed late May 2026, reopened early July with enhanced screening.
    frozenset({'cod', 'rwa'}): [('2026-05-25', '2026-07-05')],
}


@dataclass
class BorderPolicy:
    """Share of travellers crossing a border (rho), border closures by month, optional distance cost."""
    name: str = 'open'
    rho: float = 1.0                              # share of would-be cross-border travellers that crosses
    closures: dict = field(default_factory=dict)  # frozenset({code_a, code_b}) -> [(start, end|None), ...]
    closed_rho: float = 0.0                       # rho while a border is closed (0 = shut; >0 = leaky)
    extra_km: float = 0.0                         # optional: additive distance cost in the Huff choice
    factor: float = 1.0                           # optional: multiplicative distance cost in the Huff choice
    min_closed_frac: float = 0.5                  # month counts as closed if >= this share of its days is

    @classmethod
    def open(cls):
        return cls(name='open')

    @classmethod
    def crossing(cls, rho: float, name: str | None = None):
        """Share rho crosses, borders never closed."""
        return cls(name=name or f'rho{rho:g}', rho=rho)

    @classmethod
    def reported(cls, rho: float = 1.0, closed_rho: float = 0.0, name: str | None = None):
        """Share rho crosses, plus the reported closures (BORDER_CLOSURES) with closed_rho."""
        return cls(name=name or f'reported_rho{rho:g}', rho=rho, closures=dict(BORDER_CLOSURES),
                   closed_rho=closed_rho)

    @classmethod
    def closed(cls):
        """Borders closed throughout."""
        return cls(name='closed', rho=0.0)

    @classmethod
    def penalty(cls, extra_km: float = 0.0, factor: float = 1.0, name: str | None = None):
        """Secondary: distance cost in the Huff choice only (rho = 1)."""
        return cls(name=name or f'penalty_{extra_km:g}km_x{factor:g}', extra_km=extra_km, factor=factor)


# --- helpers -------------------------------------------------------------------------------------
_codes = set(countrycodes_dict.values())


def to_country_code(s: pd.Series) -> pd.Series:
    """'drc' / 'uganda' / 'cod' / 'UGA' -> ISO3 lower-case code (units use codes, airports use names)."""
    s = s.astype(str).str.lower()
    out = s.map(lambda v: v if v in _codes else countrycodes_dict.get(v, np.nan))
    if out.isna().any():
        raise ValueError(f'unknown country labels: {sorted(s[out.isna()].unique())}')
    return out


def closed_fraction(periods, month) -> float:
    """Share of the days of `month` covered by the closure periods (end=None -> still closed)."""
    m0 = pd.Timestamp(month).normalize().replace(day=1)
    days = pd.date_range(m0, m0 + pd.offsets.MonthEnd(0), freq='D')
    closed = np.zeros(len(days), bool)
    for start, end in periods:
        e = pd.Timestamp(end) if end is not None else pd.Timestamp.max.normalize()
        closed |= (days >= pd.Timestamp(start)) & (days <= e)
    return closed.mean()


def closed_pairs(policy: BorderPolicy, month) -> frozenset:
    """The border pairs that count as closed in `month`."""
    return frozenset(pair for pair, periods in policy.closures.items()
                     if closed_fraction(periods, month) >= policy.min_closed_frac)


def closed_pairs_by_month(policy: BorderPolicy, months) -> pd.DataFrame:
    """Which border pairs count as closed in which month (to check, and for the methods section)."""
    return pd.DataFrame([dict(pair='-'.join(sorted(p)), month=pd.Timestamp(t),
                              closed_frac=round(closed_fraction(per, t), 2),
                              closed=closed_fraction(per, t) >= policy.min_closed_frac)
                         for p, per in policy.closures.items() for t in months])


def _country_grid(index, columns, unit_country, airport_country):
    U = to_country_code(unit_country.reindex(index)).to_numpy()[:, None]
    A = to_country_code(airport_country.reindex(columns)).to_numpy()[None, :]
    return U, A


def border_distance(D: pd.DataFrame, unit_country: pd.Series, airport_country: pd.Series,
                    policy: BorderPolicy) -> pd.DataFrame:
    """Distance used in the open-border Huff choice (optional extra_km / factor on cross-border pairs)."""
    U, A = _country_grid(D.index, D.columns, unit_country, airport_country)
    cross = U != A
    Deff = np.where(cross, D.to_numpy() * policy.factor + policy.extra_km, D.to_numpy())
    return pd.DataFrame(Deff, index=D.index, columns=D.columns)


def no_crossing_distance(D, unit_country, airport_country) -> pd.DataFrame:
    """Distance with all cross-border pairs unreachable (inf)."""
    U, A = _country_grid(D.index, D.columns, unit_country, airport_country)
    return D.where(pd.DataFrame(U == A, index=D.index, columns=D.columns), np.inf)


def crossing_share(index, columns, unit_country, airport_country, policy: BorderPolicy,
                   closed: frozenset = frozenset()) -> pd.DataFrame:
    """unit x airport: 1 for same-country pairs, rho across an open border, closed_rho across a closed one."""
    U, A = _country_grid(index, columns, unit_country, airport_country)
    R = np.where(U == A, 1.0, policy.rho)
    for pair in closed:
        a, b = tuple(pair)
        R = np.where(((U == a) & (A == b)) | ((U == b) & (A == a)), policy.closed_rho, R)
    return pd.DataFrame(R, index=index, columns=columns)


def combine_huff(H_open: pd.DataFrame, H_none: pd.DataFrame, R: pd.DataFrame) -> pd.DataFrame:
    """H = own-country part of H_open + R * cross part of H_open + (lost share) * H_none."""
    cross = R.to_numpy() < 1.0 - 1e-12
    Ho = H_open.to_numpy()
    kept = np.where(cross, Ho * R.to_numpy(), Ho)
    lost = np.where(cross, Ho * (1.0 - R.to_numpy()), 0.0).sum(axis=1, keepdims=True)
    H = kept + lost * H_none.reindex(index=H_open.index, columns=H_open.columns).to_numpy()
    return pd.DataFrame(H, index=H_open.index, columns=H_open.columns)


# --- the border step (called from run_analysis) --------------------------------------------------
def get_border_huff(D: pd.DataFrame, S: pd.DataFrame, mode, unit_shapes, airport_shapes,
                    policy: BorderPolicy, months, **huff_kwargs):
    """
    Huff proportions with border crossings. Replaces `get_huff(D, S, mode)` in run_analysis.
    Returns (H, info):
      H    : one matrix (static, no closures) or {month: matrix}
      info : {'D_open': distance in the open-border choice, 'R': {closed pairs: crossing-share matrix},
              'closed_by_month': {month: closed pairs}}
    """
    uc = unit_shapes.drop_duplicates('unit').set_index('unit')['country']
    ac = airport_shapes.drop_duplicates('airport').set_index('airport')['country']

    D_open = border_distance(D, uc, ac, policy)
    H_open = get_huff(D_open, S, mode, reach_matrix=D, **huff_kwargs)
    H_none = get_huff(no_crossing_distance(D, uc, ac), S, mode, reach_matrix=D, **huff_kwargs)

    months = pd.DatetimeIndex(pd.to_datetime(list(months)))
    by_month = {t: closed_pairs(policy, t) for t in months}
    R = {key: crossing_share(D.index, D.columns, uc, ac, policy, key) for key in set(by_month.values())}
    info = dict(D_open=D_open, R=R, closed_by_month=by_month)

    if not isinstance(H_open, dict) and not policy.closures:          # static, nothing changes by month
        return combine_huff(H_open, H_none, R[frozenset()]), info

    if isinstance(H_open, dict):
        H_open = {pd.Timestamp(k): v for k, v in H_open.items()}
        H_none = {pd.Timestamp(k): v for k, v in H_none.items()}

    H = {}
    for t, key in by_month.items():
        Ho = H_open.get(t) if isinstance(H_open, dict) else H_open
        Hn = H_none.get(t) if isinstance(H_none, dict) else H_none
        if Ho is not None:
            H[t] = combine_huff(Ho, Hn, R[key])
    return H, info