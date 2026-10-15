"""Trading strategies on top of the de-power-spread forecast (the `engine` submodule).

The engine's paths default to a scratch folder, so it never writes into this repo's
signals/, live/, reports/ or README. Import this package before `dps`.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = Path(os.environ.get("STRATS_ENGINE", ROOT / "engine"))
if not (ENGINE / "dps" / "__init__.py").is_file():
    raise ImportError(f"engine not found in {ENGINE}: run `git submodule update --init`")
if str(ENGINE) not in sys.path:
    sys.path.insert(0, str(ENGINE))

_WORK = os.environ.get("STRATS_WORK_DIR", "work")
for key, default in (("DPS_DATA_DIR", "data"), ("DPS_REPORTS_DIR", f"{_WORK}/engine/reports"),
                     ("DPS_SIGNALS_DIR", f"{_WORK}/engine/signals"), ("DPS_LIVE_DIR", f"{_WORK}/engine/live"),
                     ("DPS_README", f"{_WORK}/engine/README.md")):
    os.environ.setdefault(key, default)
