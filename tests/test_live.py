"""Live B: same procedure as the backtest, same window, settled with the same PnL function."""
import json
from datetime import timedelta

import numpy as np
import pandas as pd

from dps import store, trading
from dps.util import issue_time
from strats import analysis, config, live, rule


def test_live_signal_equals_backtest(planted, monkeypatch):
    root, start, end = planted
    analysis.run(start, end)
    eng = pd.read_parquet(root / "engine" / "reports_dir" / "backtest.parquet")
    day = end - timedelta(days=9)
    bt = eng[(eng["strategy"] == "model") & (eng["day"] == str(day))].set_index("ts")["side"]
    assert len(bt) and (bt > 0).any()
    monkeypatch.setenv("DPS_NOW", issue_time(day).isoformat())
    out = live.signal(day)
    assert out["status"] == "written" and not out["late"]
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
