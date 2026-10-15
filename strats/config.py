"""Everything that defines strategy B and its evaluation. Fixed before the live start."""
from __future__ import annotations

import os

# --------------------------------------------------------------------------- paths
SIGNALS_DIR = os.environ.get("STRATS_SIGNALS_DIR", "signals")
LIVE_DIR = os.environ.get("STRATS_LIVE_DIR", "live")
REPORTS_DIR = os.environ.get("STRATS_REPORTS_DIR", "reports")
README = os.environ.get("STRATS_README", "README.md")

# --------------------------------------------------------------------------- strategy
NAME = "B"
LABEL = "Long-only"
# B takes the engine's positions unchanged and sets every short to zero. Nothing else:
# same model, same threshold, same size, same costs, same exit (ID-AEP).

# --------------------------------------------------------------------------- analysis
CAPS = (200.0, 100.0)          # spread capped at +-cap EUR/MWh: PnL without the spike tail
SPIKE_EUR_MWH = 200.0          # a quarter hour with |ID-AEP - DA| above this is a spike
BEST_DAYS = 10                 # PnL without the N best days
TOP_QH = 10                    # PnL of the N best quarter hours
BOOTSTRAP_DRAWS = 5000
BOOTSTRAP_BLOCK_DAYS = 5       # block bootstrap keeps the autocorrelation of daily PnL
FIXED_THRESHOLDS = (2.0, 5.0, 10.0)   # robustness: threshold not chosen monthly
ROBUST_SEEDS = (5, 6, 7, 8, 9)        # robustness: another set of five model fits

# --------------------------------------------------------------------------- live evaluation
# Written down before the first live signal of B; not changed afterwards.
EVAL_LIVE_DAYS = 120           # evaluation after this many counted live days
EVAL_T = 1.0                   # B replaces A only if B beats A at equal risk with t > EVAL_T,
                               # both uncapped and with the spread capped at +-200 EUR/MWh,
                               # and B's maximum drawdown is not worse than A's
KILL_QUANTILE = 0.05           # stop if cumulative live PnL falls below this quantile of the
                               # backtest's PnL over the same number of days
