"""Live track record of B: tomorrow's positions before the 12:00 auction, settled once the
ID-AEP is out.

signal: runs the engine's live signal (de-power-spread, unchanged) into a scratch folder and
        sets its shorts to zero. Same window as the engine, 10:45-11:50 local; a file finished
        after 11:50 is marked late and never counted. The push of signals/YYYY-MM-DD.* and the
        Actions run log are the timestamped public record.
settle: books every counted signal whose ID-AEP is known, with the engine's PnL function,
        together with its legs (A, A's shorts, always long, capped spread), into
        live/ledger.csv and the README.
"""
from __future__ import annotations

import json
import logging
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from . import ENGINE, analysis, config, rule
from dps import config as dconf
from dps import live as engine_live
from dps import store
from dps.report import _fmt, update_section
from dps.util import BERLIN, gate_closure, now, qh_index, spread_known_at

LOG = logging.getLogger(__name__)
CAP = config.CAPS[0]
COLUMNS = ["day", "late", "generated_at", "qh_long", "mwh_b", "net_b", "net_a", "net_a_short", "net_always_long",
           f"net_b_cap{int(CAP)}", f"net_a_cap{int(CAP)}", "missing_exit_qh"]


def _paths(day: date, root: str | None = None) -> tuple[Path, Path]:
    base = Path(root or config.SIGNALS_DIR) / f"{day:%Y-%m-%d}"
    return base.with_suffix(".csv"), base.with_suffix(".json")


def _tomorrow(t: pd.Timestamp) -> date:
    return t.tz_convert(BERLIN).date() + timedelta(days=1)


def status(day: date | None = None, t: pd.Timestamp | None = None) -> dict:
    """Is a signal due now? exists / too early / too late / due (cheap, no data needed)."""
    t = now() if t is None else t
    day = day or _tomorrow(t)
    opens, closes = engine_live.window(day)
    if _paths(day)[1].exists():
        s = "exists"
    elif t < opens:
        s = "too early"
    elif t > closes:
        s = "too late"
    else:
        s = "due"
    return {"status": s, "day": str(day), "opens": opens.isoformat(), "closes": closes.isoformat()}


def signal(day: date | None = None, force: bool = False) -> dict:
    t = now()
    day = day or _tomorrow(t)
    st = status(day, t)
    if st["status"] != "due" and not force:
        return st
    eng = engine_live.signal(day, force=force)
    a_csv, a_json = _paths(day, dconf.SIGNALS_DIR)
    if eng.get("status") not in ("written", "exists") or not a_json.exists():
        return {"status": f"engine: {eng.get('status')}", "day": str(day)}
    a = pd.read_csv(a_csv)
    ameta = json.loads(a_json.read_text())
    side_a = a["side"].to_numpy(dtype="float64")
    side_b = rule.long_only(side_a)
    out = pd.DataFrame({"ts_utc": a["ts_utc"], "local": a["local"], "side": side_b.astype(int),
                        "size_mw": np.where(side_b != 0, ameta["size_mw"], 0.0), "side_engine": side_a.astype(int),
                        "pred_spread_eur_mwh": a["pred_spread_eur_mwh"]})
    csv_path, meta_path = _paths(day)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(csv_path, index=False)
    written = now()                                  # lateness is judged when the file exists
    meta = {
        "strategy": config.NAME, "rule": "engine positions, every short set to zero",
        "delivery_day": str(day), "started_at": t.isoformat(), "generated_at": written.isoformat(),
        "gate_closure": gate_closure(day).isoformat(), "late": bool(written > engine_live.window(day)[1]),
        "quarter_hours": int(len(out)), "long": int((side_b > 0).sum()), "size_mw": ameta["size_mw"],
        "engine_long": int((side_a > 0).sum()), "engine_short": int((side_a < 0).sum()),
        "engine_commit": analysis._git(ENGINE),
        "engine": {k: ameta.get(k) for k in ("generated_at", "as_of", "threshold_eur_mwh", "train_days", "features",
                                             "weather_age_h", "spread_last_known_day", "hf_revisions")},
    }
    meta_path.write_text(json.dumps(meta, indent=1))
    LOG.info("signal %s: %d long (engine %d long, %d short)%s", day, meta["long"], meta["engine_long"],
             meta["engine_short"], " (LATE, not counted)" if meta["late"] else "")
    return {"status": "written", **meta}


def _counted(meta: dict) -> bool:
    if meta.get("late", False):
        return False
    try:
        return pd.Timestamp(meta["generated_at"]) < pd.Timestamp(meta["gate_closure"])
    except (KeyError, ValueError):
        return False


def kill_line(counted: pd.DataFrame) -> float | None:
    """KILL_QUANTILE of the backtest's summed PnL over windows as long as the live record."""
    p = Path(config.REPORTS_DIR) / "daily.csv"
    n = len(counted)
    if not p.is_file() or n == 0:
        return None
    b = pd.read_csv(p)["B"].astype("float64")
    if n > len(b):
        return None
    return float(b.rolling(n).sum().dropna().quantile(config.KILL_QUANTILE))


def evaluation(counted: pd.DataFrame) -> dict | None:
    """The pre-registered decision, once EVAL_LIVE_DAYS counted days exist."""
    if len(counted) < config.EVAL_LIVE_DAYS:
        return None
    c = counted.head(config.EVAL_LIVE_DAYS)
    raw = analysis.paired(c["net_b"].reset_index(drop=True), c["net_a"].reset_index(drop=True))
    cap = analysis.paired(c[f"net_b_cap{int(CAP)}"].reset_index(drop=True), c[f"net_a_cap{int(CAP)}"].reset_index(drop=True))
    dd_b = float((c["net_b"].cumsum() - c["net_b"].cumsum().cummax().clip(lower=0)).min())
    dd_a = float((c["net_a"].cumsum() - c["net_a"].cumsum().cummax().clip(lower=0)).min())
    ok = bool((raw["t_equal_risk"] or -9) > config.EVAL_T and (cap["t_equal_risk"] or -9) > config.EVAL_T and dd_b >= dd_a)
    return {"t_equal_risk": raw["t_equal_risk"], "t_equal_risk_capped": cap["t_equal_risk"], "maxdd_b": dd_b, "maxdd_a": dd_a,
            "b_replaces_a": ok}


def settle() -> dict:
    """Recompute the ledger from all signal files whose ID-AEP is known."""
    t = now()
    da = store.read("da").set_index("ts")["da"].astype("float64")
    ida = store.read("id_aep").set_index("ts")["id_aep"].astype("float64")
    rows, pending, signal_days = [], [], []
    for meta_path in sorted(Path(config.SIGNALS_DIR).glob("*.json")):
        meta = json.loads(meta_path.read_text())
        day = date.fromisoformat(meta["delivery_day"])
        signal_days.append(day)
        sig = pd.read_csv(meta_path.with_suffix(".csv"))
        idx = pd.DatetimeIndex(pd.to_datetime(sig["ts_utc"], utc=True))
        m = pd.DataFrame({"day": str(day), "da": da.reindex(idx).to_numpy(), "id_aep": ida.reindex(idx).to_numpy()})
        complete = m["id_aep"].notna().sum() >= 0.9 * len(qh_index(day))
        if m["da"].isna().all() or not (complete or t >= spread_known_at(day) + pd.Timedelta(days=1)):
            pending.append(str(day))
            continue
        legs = rule.legs(sig["side_engine"].to_numpy())
        assert np.array_equal(legs["B"], sig["side"].to_numpy(dtype="float64")), f"{day}: B is not the engine without shorts"
        r = {k: analysis.leg_pnl(s, m) for k, s in legs.items()}
        rows.append({"day": str(day), "late": not _counted(meta), "generated_at": meta["generated_at"],
                     "qh_long": int((legs["B"] > 0).sum()), "mwh_b": float(r["B"]["mwh"].sum()),
                     "net_b": round(float(r["B"]["net"].sum()), 2), "net_a": round(float(r["A"]["net"].sum()), 2),
                     "net_a_short": round(float(r["A_short"]["net"].sum()), 2),
                     "net_always_long": round(float(r["always_long"]["net"].sum()), 2),
                     f"net_b_cap{int(CAP)}": round(float(analysis.leg_pnl(legs["B"], m, CAP)["net"].sum()), 2),
                     f"net_a_cap{int(CAP)}": round(float(analysis.leg_pnl(legs["A"], m, CAP)["net"].sum()), 2),
                     "missing_exit_qh": int(r["B"]["missing_exit"].sum())})
    ledger = pd.DataFrame(rows, columns=COLUMNS)
    live = Path(config.LIVE_DIR)
    live.mkdir(parents=True, exist_ok=True)
    ledger.to_csv(live / "ledger.csv", index=False)
    missing = engine_live.missing_days(signal_days, t)
    body = live_markdown(ledger, pending, missing)
    (live / "SUMMARY.md").write_text("# Live-Track-Record: B (Long-only)\n\n" + body)
    update_section(Path(config.README), "LIVE", body)
    counted = ledger[~ledger["late"].astype(bool)] if not ledger.empty else ledger
    return {"settled_days": int(len(counted)), "pending": pending, "missing": missing,
            "net_b": round(float(counted["net_b"].sum()), 2) if len(counted) else 0.0,
            "net_a": round(float(counted["net_a"].sum()), 2) if len(counted) else 0.0}


def _days(n: int) -> str:
    return f"{n} Tag" if n == 1 else f"{n} Tage"


def live_markdown(ledger: pd.DataFrame, pending: list[str], missing: list[str] = ()) -> str:
    f = _fmt
    counted = ledger[~ledger["late"].astype(bool)] if not ledger.empty else ledger
    late = ledger[ledger["late"].astype(bool)] if not ledger.empty else ledger
    notes = []
    if len(late):
        notes.append(f"Nach 11:50 fertig und deshalb nicht gezählt: {', '.join(late['day'])}")
    if missing:
        notes.append(f"Kein Signal (kein Lauf rechtzeitig gestartet oder Data Guard, Grund im Actions-Log): {', '.join(missing)}")
    if pending:
        notes.append(f"Warten auf ID-AEP: {', '.join(pending)}")
    tail = "".join(f"\n\n{n}" for n in notes)
    if counted.empty:
        return ("_Noch kein abgerechneter Tag. Signale liegen in `signals/`, abgerechnet wird, sobald der ID-AEP "
                "veröffentlicht ist._" + tail + "\n")
    n = len(counted)
    b, a = counted["net_b"], counted["net_a"]
    mwh = float(counted["mwh_b"].sum())
    per = f" ({f(b.sum() / mwh, 2, True)} €/MWh)" if mwh else ""
    cap = f"net_b_cap{int(CAP)}"
    lines = [
        f"{_days(n)} abgerechnet ({counted['day'].min()} bis {counted['day'].max()}).", "",
        "| | B: Long-only | A: Engine (Referenz) | A's Shorts | immer long |", "|---|---:|---:|---:|---:|",
        f"| Netto € | **{f(b.sum(), 0, True)}**{per} | {f(a.sum(), 0, True)} | {f(counted['net_a_short'].sum(), 0, True)} | "
        f"{f(counted['net_always_long'].sum(), 0, True)} |",
        f"| Spread gekappt ±{int(CAP)} €/MWh | {f(counted[cap].sum(), 0, True)} | "
        f"{f(counted[f'net_a_cap{int(CAP)}'].sum(), 0, True)} | | |",
        f"| Tage im Plus | {int((b > 0).sum())} von {n} | {int((a > 0).sum())} von {n} | | |", "",
    ]
    kl = kill_line(counted)
    if kl is not None:
        state = "unterschritten: B wird eingestellt" if b.sum() < kl else "nicht erreicht"
        lines.append(f"Abbruchgrenze nach {_days(n)} ({f(100 * config.KILL_QUANTILE, 0)}-%-Quantil des Backtests über "
                     f"gleich lange Zeiträume): {f(kl, 0, True)} €, {state}.")
    ev = evaluation(counted)
    if ev is None:
        lines.append(f"Vorab festgelegte Auswertung nach {config.EVAL_LIVE_DAYS} gezählten Tagen: {n} von "
                     f"{config.EVAL_LIVE_DAYS}.")
    else:
        verdict = "B ersetzt A" if ev["b_replaces_a"] else "A bleibt"
        lines.append(f"Auswertung nach {config.EVAL_LIVE_DAYS} Tagen: t bei gleichem Risiko {f(ev['t_equal_risk'], 2)}, "
                     f"gekappt {f(ev['t_equal_risk_capped'], 2)}; Max. Drawdown B {f(ev['maxdd_b'], 0, True)} €, "
                     f"A {f(ev['maxdd_a'], 0, True)} €. **{verdict}.**")
    lines += ["", "| Liefertag | Signal fertig (UTC) | Long-Viertelstunden | B € | A € | immer long € | B kumuliert € |",
              "|---|---|---:|---:|---:|---:|---:|"]
    cum = b.cumsum()
    for i, r in counted.tail(14).iterrows():
        gen = pd.Timestamp(r["generated_at"]).tz_convert("UTC").strftime("%Y-%m-%d %H:%M")
        lines.append(f"| {r['day']} | {gen} | {r['qh_long']} | {f(r['net_b'], 0, True)} | {f(r['net_a'], 0, True)} | "
                     f"{f(r['net_always_long'], 0, True)} | {f(cum[i], 0, True)} |")
    return "\n".join(lines) + tail + "\n"
