"""Backtest of B: the engine's walk-forward (de-power-spread, unchanged), its positions with
the shorts removed, and the breakdown into legs. Writes reports/backtest.json and
reports/daily.csv; strats.report renders them.
"""
from __future__ import annotations

import json
import logging
import subprocess
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

from . import ENGINE, ROOT, config, rule
from dps import backtest as engine_backtest
from dps import config as dconf
from dps import metrics, store, trading
from dps.util import BERLIN, now

LOG = logging.getLogger(__name__)


# --------------------------------------------------------------------------- engine
def engine_run(start: date, end: date, seeds: tuple[int, ...] | None = None) -> tuple[dict, pd.DataFrame]:
    """The engine's walk-forward backtest; returns its summary and the model's quarter hours."""
    old = dconf.MODEL_SEEDS
    try:
        if seeds is not None:
            dconf.MODEL_SEEDS = tuple(seeds)
        out = engine_backtest.run(start, end)
        res = pd.read_parquet(Path(dconf.REPORTS_DIR) / "backtest.parquet")
    finally:
        dconf.MODEL_SEEDS = old
    m = res[res["strategy"] == "model"].copy()
    m["ts"] = pd.to_datetime(m["ts"], utc=True)
    m["day"] = m["day"].astype(str)
    m = m.rename(columns={"side": "side_a"})
    return out, m.sort_values("ts").reset_index(drop=True)[["ts", "day", "side_a", "pred", "da", "id_aep"]]


# --------------------------------------------------------------------------- PnL
def leg_pnl(side, m: pd.DataFrame, cap: float | None = None) -> pd.DataFrame:
    """Per quarter hour, with the engine's PnL function. cap: spread clipped at +-cap."""
    da = m["da"].to_numpy(dtype="float64")
    exit_ = m["id_aep"].to_numpy(dtype="float64")
    if cap is not None:
        exit_ = da + np.clip(exit_ - da, -cap, cap)
    r = trading.pnl(side, da, exit_)
    r["day"] = m["day"].to_numpy()
    r["side"] = np.asarray(side, dtype="float64")
    r["da"] = da
    return r


def daily(r: pd.DataFrame, days: list[str]) -> pd.Series:
    return r.groupby("day")["net"].sum().reindex(days, fill_value=0.0)


def _sharpe(d: pd.Series) -> float | None:
    s = float(d.std(ddof=1)) if len(d) > 1 else 0.0
    return round(float(d.mean()) / s * np.sqrt(365), 2) if s > 0 else None


def _t(d: pd.Series) -> float | None:
    return metrics._num(metrics.hac_t(np.asarray(d, dtype="float64")), 2)


def leg_stats(r: pd.DataFrame, days: list[str]) -> dict:
    s = metrics.summary(r, days)
    d = daily(r, days)
    half = len(days) // 2
    mwh = float(r["mwh"].sum())
    s.update({
        "without_best_days_eur": round(float(d.sum() - d.nlargest(config.BEST_DAYS).sum()), 0),
        "top_qh_net_eur": round(float(r["net"].nlargest(config.TOP_QH).sum()), 0),
        "break_even_slippage_eur_mwh": round(float(r["gross"].sum() - r["fees"].sum()) / mwh, 2) if mwh else None,
        "sharpe_first_half": _sharpe(d.iloc[:half]),
        "sharpe_second_half": _sharpe(d.iloc[half:]),
        "positive_months": int((d.groupby(pd.to_datetime(pd.Series(days)).dt.strftime("%Y-%m").to_numpy()).sum() > 0).sum()),
        "months": int(pd.to_datetime(pd.Series(days)).dt.strftime("%Y-%m").nunique()),
    })
    return s


def paired(a: pd.Series, b: pd.Series, draws: int = config.BOOTSTRAP_DRAWS, block: int = config.BOOTSTRAP_BLOCK_DAYS,
           seed: int = 0) -> dict:
    """a against b on daily PnL: raw difference, difference at equal risk (a scaled to b's
    volatility), and a block bootstrap of the Sharpe difference."""
    a, b = a.astype("float64"), b.astype("float64")
    raw = a - b
    eq = (a * (b.std() / a.std()) - b) if a.std() > 0 else raw
    rng = np.random.default_rng(seed)
    x, y, n = a.to_numpy(), b.to_numpy(), len(a)
    diffs = []
    for _ in range(draws):
        starts = rng.integers(0, n, n // block + 1)
        idx = (starts[:, None] + np.arange(block)[None, :]).ravel()[:n] % n
        xs, ys = x[idx], y[idx]
        sx, sy = xs.std(ddof=1), ys.std(ddof=1)
        if sx > 0 and sy > 0:
            diffs.append((xs.mean() / sx - ys.mean() / sy) * np.sqrt(365))
    diffs = np.array(diffs)
    return {"mean_diff_eur_per_day": metrics._num(raw.mean(), 1), "t_raw": _t(raw), "t_equal_risk": _t(eq),
            "sharpe_diff": metrics._num((_sharpe(a) or 0) - (_sharpe(b) or 0), 2),
            "p_sharpe_higher": metrics._num(float((diffs > 0).mean()), 2) if len(diffs) else None,
            "sharpe_diff_ci90": [metrics._num(float(q), 2) for q in np.percentile(diffs, [5, 95])] if len(diffs) else None}


# --------------------------------------------------------------------------- the market
def anatomy(start: date, end: date) -> dict:
    """What the spread ID-AEP - DA looks like: median, mean and where the mean comes from."""
    da = store.read("da").set_index("ts")["da"]
    ida = store.read("id_aep").set_index("ts")["id_aep"]
    lo = pd.Timestamp(start.isoformat(), tz=BERLIN).tz_convert("UTC")
    hi = pd.Timestamp(end.isoformat(), tz=BERLIN).tz_convert("UTC")
    s = (ida - da).dropna()
    s = s[(s.index >= lo) & (s.index < hi)]
    if s.empty:
        return {}
    top = s[s >= s.quantile(0.99)]
    body = s[s.abs() <= 100]
    hour = s.index.tz_convert(BERLIN).hour
    by_hour = pd.DataFrame({"mean": s.groupby(hour).mean(), "median": s.groupby(hour).median(),
                            "up": (s > config.SPIKE_EUR_MWH).groupby(hour).sum(),
                            "down": (s < -config.SPIKE_EUR_MWH).groupby(hour).sum()})
    trim = s[(s > s.quantile(0.05)) & (s < s.quantile(0.95))]
    return {
        "from": str(start), "to": str(end), "quarter_hours": int(len(s)),
        "mean": round(float(s.mean()), 2), "median": round(float(s.median()), 2),
        "trimmed_mean_5": round(float(trim.mean()), 2), "body_mean_abs_le_100": round(float(body.mean()), 2),
        "share_positive": round(float((s > 0).mean()), 3),
        "top1pct_share_of_sum": round(float(top.sum() / s.sum()), 2) if s.sum() > 0 else None,
        "spikes_up": int((s > config.SPIKE_EUR_MWH).sum()), "spikes_down": int((s < -config.SPIKE_EUR_MWH).sum()),
        "spike_days": int(pd.Series(s.index.tz_convert(BERLIN).date)[(s > config.SPIKE_EUR_MWH).to_numpy()].nunique()),
        "by_hour": {int(h): {k: round(float(v), 1) for k, v in row.items()} for h, row in by_hour.iterrows()},
    }


# --------------------------------------------------------------------------- provenance
def _git(path: Path) -> str | None:
    try:
        sha = subprocess.run(["git", "-C", str(path), "rev-parse", "HEAD"], capture_output=True, text=True,
                             check=True).stdout.strip()
        dirty = subprocess.run(["git", "-C", str(path), "status", "--porcelain", "--untracked-files=no"],
                               capture_output=True, text=True).stdout.strip()
        return sha + ("+dirty" if dirty else "")
    except (OSError, subprocess.CalledProcessError):
        return None


# --------------------------------------------------------------------------- run
def run(start: date | None = None, end: date | None = None, robustness: bool = False) -> dict:
    start = start or dconf.START
    end = end or engine_backtest.default_end()
    eng, m = engine_run(start, end)
    days = sorted(m["day"].unique())
    sides = rule.legs(m["side_a"].to_numpy())
    pnl = {k: leg_pnl(s, m) for k, s in sides.items()}
    dly = {k: daily(r, days) for k, r in pnl.items()}
    out = {
        "generated_at": now().isoformat(),
        "test_period": {"from": days[0], "to": days[-1], "days": len(days)},
        "assumptions": eng["assumptions"],
        "engine_months": [{k: mo[k] for k in ("month", "train_days", "train_last_day", "threshold")} for mo in eng["months"]],
        "legs": {k: leg_stats(r, days) for k, r in pnl.items()},
        "capped": {}, "paired": {}, "monthly": {},
    }
    capped_daily = {}
    for k in ("B", "A", "always_long"):
        out["capped"][k] = {}
        for cap in config.CAPS:
            d = daily(leg_pnl(sides[k], m, cap), days)
            capped_daily[(k, cap)] = d
            out["capped"][k][str(int(cap))] = {"net_eur": round(float(d.sum()), 0), "t_daily_hac": _t(d), "sharpe_daily_ann": _sharpe(d)}
    out["paired"]["B_vs_A"] = paired(dly["B"], dly["A"])
    out["paired"]["B_vs_always_long"] = paired(dly["B"], dly["always_long"])
    c = int(config.CAPS[0])
    out["paired"][f"B_vs_A_capped_{c}"] = paired(capped_daily[("B", config.CAPS[0])], capped_daily[("A", config.CAPS[0])])
    months = pd.to_datetime(pd.Series(days)).dt.strftime("%Y-%m").to_numpy()
    for k in ("B", "A", "always_long"):
        for mo, v in dly[k].groupby(months).sum().items():
            out["monthly"].setdefault(mo, {})[k] = round(float(v), 0)
    out["anatomy"] = anatomy(start, end)
    if robustness:
        out["robustness"] = robustness_checks(m, days, start, end)
    out["provenance"] = {"strats_commit": _git(ROOT), "engine_commit": _git(ENGINE),
                         "engine_provenance": eng.get("provenance", {})}
    rep = Path(config.REPORTS_DIR)
    rep.mkdir(parents=True, exist_ok=True)
    table = pd.DataFrame({k: dly[k] for k in rule.LEGS})
    for cap in config.CAPS[:1]:
        table[f"B_cap{int(cap)}"] = capped_daily[("B", cap)]
        table[f"A_cap{int(cap)}"] = capped_daily[("A", cap)]
    table.round(2).rename_axis("day").to_csv(rep / "daily.csv")
    (rep / "backtest.json").write_text(json.dumps(out, indent=1, default=str))
    b, a = out["legs"]["B"], out["legs"]["A"]
    LOG.info("B: net %.0f EUR, Sharpe %s, t %s | A: net %.0f EUR, Sharpe %s, t %s", b["net_eur"], b["sharpe_daily_ann"],
             b["t_daily_hac"], a["net_eur"], a["sharpe_daily_ann"], a["t_daily_hac"])
    return out


def robustness_checks(m: pd.DataFrame, days: list[str], start: date, end: date) -> dict:
    """Does B depend on the monthly threshold or on the particular five model fits?"""
    rows = {}
    for th in config.FIXED_THRESHOLDS:
        side = np.where(m["pred"].to_numpy() > th, 1.0, 0.0)
        d = daily(leg_pnl(side, m), days)
        dc = daily(leg_pnl(side, m, config.CAPS[0]), days)
        rows[f"threshold_{th:g}"] = {"label": f"feste Schwelle {th:g} €/MWh", "net_eur": round(float(d.sum()), 0),
                                     "sharpe_daily_ann": _sharpe(d), "t_daily_hac": _t(d), "capped_t": _t(dc)}
    _, m2 = engine_run(start, end, seeds=config.ROBUST_SEEDS)
    m2 = m2.set_index("ts").reindex(m["ts"]).reset_index()
    for k, s in (("B", rule.long_only(m2["side_a"].fillna(0).to_numpy())), ("A", m2["side_a"].fillna(0).to_numpy())):
        d = daily(leg_pnl(s, m), days)
        dc = daily(leg_pnl(s, m, config.CAPS[0]), days)
        seeds = f"{config.ROBUST_SEEDS[0]}–{config.ROBUST_SEEDS[-1]}"
        rows[f"seeds_{k}"] = {"label": f"{k}, Seeds {seeds}", "net_eur": round(float(d.sum()), 0),
                              "sharpe_daily_ann": _sharpe(d), "t_daily_hac": _t(d), "capped_t": _t(dc)}
    return rows
