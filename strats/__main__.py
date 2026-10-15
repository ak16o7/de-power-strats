"""python -m strats <command>

  fetch      prices, load and ID-AEP into data/ (the engine's fetcher; API keys optional)
  backtest   engine walk-forward, strategy B and its legs -> reports/, README (--robustness: more checks)
  report     re-render reports/REPORT.md, the chart and the README from reports/backtest.json
  status     live: is a signal due now? (exists / too early / too late / due)
  signal     live: tomorrow's positions of B -> signals/YYYY-MM-DD.csv (10:45-11:50 local)
  settle     live: book signals whose ID-AEP is out -> live/ledger.csv, README
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date

from . import analysis, config, live, report  # noqa: F401  (importing strats wires the engine)
from dps import util


def _date(s: str | None) -> date | None:
    return date.fromisoformat(s) if s else None


def main(argv: list[str] | None = None) -> int:
    util.setup_logging()
    ap = argparse.ArgumentParser(prog="strats", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch")
    f.add_argument("--full", action="store_true", help="refetch everything since the engine's START")
    f.add_argument("--recent-days", type=int, default=7)
    b = sub.add_parser("backtest")
    b.add_argument("--start")
    b.add_argument("--end", help="exclusive delivery day")
    b.add_argument("--robustness", action="store_true", help="fixed thresholds and a second set of model seeds")
    sub.add_parser("report")
    st = sub.add_parser("status")
    st.add_argument("--github-output", action="store_true", help="append due=true|false to $GITHUB_OUTPUT")
    s = sub.add_parser("signal")
    s.add_argument("--day", help="delivery day, default tomorrow")
    s.add_argument("--force", action="store_true", help="ignore the time window (late signals are never counted)")
    sub.add_parser("settle")
    a = ap.parse_args(argv)

    if a.cmd == "fetch":
        from dps import fetch
        rep = fetch.run(full=a.full, recent_days=a.recent_days)
        print(json.dumps(rep, indent=1))
        return 1 if all(v.startswith("ERROR") for v in rep.values()) else 0
    if a.cmd == "backtest":
        analysis.run(_date(a.start), _date(a.end), robustness=a.robustness)
        report.run()
    if a.cmd == "report":
        report.run()
    if a.cmd == "status":
        res = live.status()
        print(json.dumps(res, indent=1))
        if a.github_output and os.environ.get("GITHUB_OUTPUT"):
            with open(os.environ["GITHUB_OUTPUT"], "a") as fh:
                fh.write(f"due={'true' if res['status'] == 'due' else 'false'}\n")
    if a.cmd == "signal":
        print(json.dumps(live.signal(_date(a.day), force=a.force), indent=1, default=str))
    if a.cmd == "settle":
        print(json.dumps(live.settle(), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
