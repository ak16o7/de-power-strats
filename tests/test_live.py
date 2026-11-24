"""Live B: same procedure as the backtest, same window, settled with the same PnL function."""
import json
from datetime import timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from dps import config as dconf
from dps import live as engine_live
from dps import store, trading
from dps.util import issue_time
from strats import analysis, config, live, rule


def serve(monkeypatch, **dirs):
    """Serve the engine repository's files from local folders: serve(signals=..., models=...)."""
    def fake(path):
        folder, name = path.rsplit("/", 1)
        base = dirs.get(folder.split("/")[-1])
        f = Path(base) / name if base else None
        return f.read_bytes() if f is not None and f.is_file() else None
    monkeypatch.setattr(live, "_engine_file", fake)


def test_live_signal_equals_backtest(planted, monkeypatch):
    """Own engine run (nothing published): B is still the backtest's engine without shorts."""
    root, start, end = planted
    monkeypatch.setattr(config, "ENGINE_FALLBACK_MIN_AFTER_ISSUE", -60)
    analysis.run(start, end)
    eng = pd.read_parquet(root / "engine" / "reports_dir" / "backtest.parquet")
    day = end - timedelta(days=9)
    bt = eng[(eng["strategy"] == "model") & (eng["day"] == str(day))].set_index("ts")["side"]
    assert len(bt) and (bt > 0).any()
    monkeypatch.setenv("DPS_NOW", issue_time(day).isoformat())
    out = live.signal(day)
    assert out["status"] == "written" and not out["late"] and out["engine_source"] == "own_run"
    sig = pd.read_csv(root / "signals" / f"{day}.csv")
    side = pd.Series(sig["side"].to_numpy(dtype=float), index=pd.to_datetime(sig["ts_utc"], utc=True))
    assert np.array_equal(side.to_numpy(), rule.long_only(bt.reindex(side.index).to_numpy()))
    assert np.array_equal(sig["side"].to_numpy(), rule.long_only(sig["side_engine"].to_numpy()))
    assert live.signal(day)["status"] == "exists"


def test_status_gate(planted, monkeypatch):
    root, start, end = planted
    day = end - timedelta(days=4)
    issue = issue_time(day)
    for minutes, expect in ((-30, "too early"), (-10, "due"), (49, "due"), (51, "too late")):
        monkeypatch.setenv("DPS_NOW", (issue + pd.Timedelta(minutes=minutes)).isoformat())
        assert live.status(day)["status"] == expect, minutes


def test_late_signal_is_not_counted(planted, monkeypatch):
    root, start, end = planted
    day = end - timedelta(days=6)
    issue = issue_time(day)
    monkeypatch.setenv("DPS_NOW", (issue + pd.Timedelta(minutes=40)).isoformat())
    clock = iter([issue + pd.Timedelta(minutes=40)] + [issue + pd.Timedelta(minutes=55)] * 20)
    monkeypatch.setattr("strats.live.now", lambda: next(clock))
    out = live.signal(day)
    assert out["status"] == "written" and out["late"]
    monkeypatch.setattr("strats.live.now", lambda: pd.Timestamp(f"{day + timedelta(days=3)}T12:00:00", tz="UTC"))
    res = live.settle()
    assert res["settled_days"] == 0
    assert "nicht gezählt" in (root / "live" / "SUMMARY.md").read_text()


def test_settlement_and_legs(planted, monkeypatch):
    root, start, end = planted
    monkeypatch.setattr(config, "ENGINE_FALLBACK_MIN_AFTER_ISSUE", -60)
    d1, d2 = end - timedelta(days=8), end - timedelta(days=6)        # d1 + 1 day has no signal
    for d in (d1, d2):
        monkeypatch.setenv("DPS_NOW", (issue_time(d) - pd.Timedelta(minutes=5)).isoformat())
        assert live.signal(d)["status"] == "written"
    monkeypatch.setenv("DPS_NOW", f"{d2 + timedelta(days=3)}T12:00:00+00:00")
    res = live.settle()
    assert res["settled_days"] == 2 and str(d1 + timedelta(days=1)) in res["missing"]
    led = pd.read_csv(root / "live" / "ledger.csv")
    assert np.allclose(led["net_a"], led["net_b"] + led["net_a_short"], atol=0.02)
    sig = pd.read_csv(root / "signals" / f"{d1}.csv")
    idx = pd.DatetimeIndex(pd.to_datetime(sig["ts_utc"], utc=True))
    da = store.read("da").set_index("ts")["da"].reindex(idx)
    ida = store.read("id_aep").set_index("ts")["id_aep"].reindex(idx)
    expect = trading.pnl(sig["side"], da, ida)["net"].sum()
    assert led.loc[led["day"] == str(d1), "net_b"].iloc[0] == round(float(expect), 2)
    readme = (root / "README.md").read_text()
    assert "2 Tage abgerechnet" in readme and "Kein Signal" in readme
    assert json.loads((root / "signals" / f"{d1}.json").read_text())["strategy"] == "B"


def test_kill_line_and_evaluation(planted, monkeypatch):
    root, start, end = planted
    (root / "reports").mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"day": range(300), "B": np.r_[np.full(150, 100.0), np.full(150, -100.0)]}).to_csv(root / "reports" / "daily.csv", index=False)
    led = pd.DataFrame({"net_b": np.ones(10), "net_a": np.zeros(10)})
    assert live.kill_line(led) == -1000.0
    assert live.evaluation(led) is None
    n = config.EVAL_LIVE_DAYS
    rng = np.random.default_rng(0)
    a = rng.normal(0, 100, n)
    b = a + 50 + rng.normal(0, 20, n)          # B = A plus a clear edge
    big = pd.DataFrame({"net_b": b, "net_a": a, "net_b_cap200": b, "net_a_cap200": a})
    ev = live.evaluation(big)
    assert ev["b_replaces_a"] is True
    assert live.evaluation(big.rename(columns={"net_b": "net_a", "net_a": "net_b", "net_b_cap200": "net_a_cap200",
                                               "net_a_cap200": "net_b_cap200"}))["b_replaces_a"] is False


def test_b_is_built_from_the_published_engine_signal(planted, monkeypatch, tmp_path):
    """The engine's own record is the source of A: no engine run here, positions identical."""
    root, start, end = planted
    day = end - timedelta(days=9)
    monkeypatch.setenv("DPS_NOW", issue_time(day).isoformat())
    monkeypatch.setattr(dconf, "SIGNALS_DIR", str(tmp_path / "spread_signals"))   # de-power-spread's repo
    monkeypatch.setattr(dconf, "LIVE_DIR", str(tmp_path / "spread_live"))
    assert engine_live.signal(day)["status"] == "written"
    serve(monkeypatch, signals=tmp_path / "spread_signals")
    runs = []
    monkeypatch.setattr(engine_live, "signal", lambda *a, **k: runs.append(a) or {"status": "x"})
    monkeypatch.setenv("DPS_NOW", (issue_time(day) + pd.Timedelta(minutes=8)).isoformat())
    out = live.signal(day)
    assert out["status"] == "written" and out["engine_source"] == "published" and runs == []
    a = pd.read_csv(tmp_path / "spread_signals" / f"{day}.csv")
    b = pd.read_csv(root / "signals" / f"{day}.csv")
    assert np.array_equal(b["side_engine"], a["side"]) and np.array_equal(b["side"], rule.long_only(a["side"]))
    assert out["engine"]["model"]["file"] == f"models/{day:%Y-%m}.pkl.gz" and out["engine_commit"] is None


def test_waits_for_the_engine_then_runs_it_with_its_month_model(planted, monkeypatch, tmp_path):
    root, start, end = planted
    d0, day = end - timedelta(days=10), end - timedelta(days=9)
    assert d0.month == day.month
    # de-power-spread has fitted this month's model (signal of d0) but not yet published day's signal
    monkeypatch.setattr(dconf, "SIGNALS_DIR", str(tmp_path / "spread_signals"))
    monkeypatch.setattr(dconf, "LIVE_DIR", str(tmp_path / "spread_live"))
    monkeypatch.setenv("DPS_NOW", issue_time(d0).isoformat())
    assert engine_live.signal(d0)["status"] == "written"
    serve(monkeypatch, signals=tmp_path / "spread_signals", models=tmp_path / "spread_live" / "models")
    monkeypatch.setattr(dconf, "SIGNALS_DIR", str(tmp_path / "scratch_signals"))  # this repo's scratch folder
    monkeypatch.setattr(dconf, "LIVE_DIR", str(tmp_path / "scratch_live"))
    monkeypatch.setenv("DPS_NOW", (issue_time(day) + pd.Timedelta(minutes=5)).isoformat())
    out = live.signal(day)
    assert out["status"].startswith("waiting") and not (root / "signals" / f"{day}.csv").exists()
    monkeypatch.setenv("DPS_NOW", (issue_time(day) + pd.Timedelta(minutes=20)).isoformat())
    out = live.signal(day)
    assert out["status"] == "written" and out["engine_source"] == "own_run" and out["engine_commit"]
    assert out["engine"]["model"]["loaded"] is True                        # the engine's frozen model
    assert out["engine"]["model"]["trained_for_day"] == str(d0)
    note = live.live_markdown(pd.DataFrame([{"day": str(day), "late": False, "net_b": 1.0, "net_a": 1.0, "net_a_short": 0.0,
                                             "net_always_long": 0.0, "mwh_b": 1.0, "qh_long": 1, "generated_at": "2026-02-18T10:20:00+00:00",
                                             "net_b_cap200": 1.0, "net_a_cap200": 1.0, "missing_exit_qh": 0,
                                             "engine_source": "own_run"}]), [])
    assert "selbst gerechnet" in note and str(day) in note


def test_an_inconsistent_published_signal_is_not_used(planted, monkeypatch, tmp_path):
    root, start, end = planted
    day = end - timedelta(days=9)
    (tmp_path / "pub").mkdir()
    (tmp_path / "pub" / f"{day}.json").write_text(json.dumps({"delivery_day": str(day - timedelta(days=1))}))
    (tmp_path / "pub" / f"{day}.csv").write_text("ts_utc,local,side,size_mw,pred_spread_eur_mwh\n")
    serve(monkeypatch, signals=tmp_path / "pub")
    assert live.published_signal(day) is None
