"""The backtest of B is the engine's backtest with the shorts removed, nothing else."""
import json

import numpy as np
import pandas as pd

from strats import analysis, report


def test_b_is_the_engine_without_shorts(planted):
    root, start, end = planted
    bt = analysis.run(start, end)
    eng = pd.read_parquet(root / "engine" / "reports_dir" / "backtest.parquet")
    m = eng[eng["strategy"] == "model"]
    assert bt["legs"]["B"]["net_eur"] == round(float(m.loc[m["side"] > 0, "net"].sum()), 0)
    assert bt["legs"]["A"]["net_eur"] == round(float(m["net"].sum()), 0)
    d = pd.read_csv(root / "reports" / "daily.csv")
    assert np.allclose(d["A"], d["B"] + d["A_short"], atol=0.02)
    assert bt["legs"]["B"]["mwh"] <= bt["legs"]["A"]["mwh"]
    al = eng[eng["strategy"] == "always_long"]
    assert bt["legs"]["always_long"]["net_eur"] == round(float(al["net"].sum()), 0)


def test_capped_and_paired_are_consistent(planted):
    root, start, end = planted
    bt = analysis.run(start, end)
    an = bt["anatomy"]
    assert an["quarter_hours"] > 0 and len(an["by_hour"]) == 24
    assert an["spikes_up"] >= 0 and an["spikes_down"] >= 0
    for k in ("B", "A", "always_long"):
        assert set(bt["capped"][k]) == {"200", "100"}
    p = bt["paired"]["B_vs_A"]
    assert 0 <= p["p_sharpe_higher"] <= 1 and p["sharpe_diff_ci90"][0] <= p["sharpe_diff_ci90"][1]
    same = analysis.paired(pd.Series(np.arange(30.0) % 7 - 3), pd.Series(np.arange(30.0) % 7 - 3))
    assert same["mean_diff_eur_per_day"] == 0.0


def test_report_renders(planted):
    root, start, end = planted
    analysis.run(start, end)
    body = report.run()
    text = (root / "README.md").read_text()
    assert "B: Long-only" in body and "nan" not in body.lower()
    assert "Median" in text and "B: Long-only" in text
    assert (root / "reports" / "pnl.png").stat().st_size > 10_000
    assert "Monate" in (root / "reports" / "REPORT.md").read_text()
    json.loads((root / "reports" / "backtest.json").read_text())
