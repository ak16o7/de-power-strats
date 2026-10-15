"""A synthetic world from the engine (no network), wired into the engine's and our config."""
from __future__ import annotations

from datetime import timedelta
from pathlib import Path

import pytest

import strats  # noqa: F401  (puts the engine on the path)
from dps import config as dconf
from dps import hf, synthetic
from strats import config

DAYS = 150


@pytest.fixture(autouse=True)
def one_seed(monkeypatch):
    """The engine averages five fits; one keeps the synthetic tests fast."""
    monkeypatch.setattr(dconf, "MODEL_SEEDS", (0,))


@pytest.fixture(scope="session")
def world(tmp_path_factory):
    root = tmp_path_factory.mktemp("world")
    start = dconf.START
    end = start + timedelta(days=DAYS)
    synthetic.make(root / "data", root / "hf", start, end, alpha=True, seed=7)
    return root, start, end


README = "# x\n<!-- RESULTS:START -->\n<!-- RESULTS:END -->\n<!-- ANATOMY:START -->\n<!-- ANATOMY:END -->\n" \
         "<!-- LIVE:START -->\n<!-- LIVE:END -->\n"


@pytest.fixture
def planted(world, tmp_path, monkeypatch):
    """Shared synthetic data, outputs in a fresh folder per test."""
    root, start, end = world
    monkeypatch.setattr(dconf, "DATA_DIR", str(root / "data"))
    for name in ("REPORTS_DIR", "SIGNALS_DIR", "LIVE_DIR"):
        monkeypatch.setattr(dconf, name, str(tmp_path / "engine" / name.lower()))
    monkeypatch.setattr(dconf, "README", str(tmp_path / "engine" / "README.md"))
    monkeypatch.setattr(config, "SIGNALS_DIR", str(tmp_path / "signals"))
    monkeypatch.setattr(config, "LIVE_DIR", str(tmp_path / "live"))
    monkeypatch.setattr(config, "REPORTS_DIR", str(tmp_path / "reports"))
    monkeypatch.setattr(config, "README", str(tmp_path / "README.md"))
    (tmp_path / "README.md").write_text(README)
    monkeypatch.setenv("DPS_HF_LOCAL", str(root / "hf"))
    hf.weather.cache_clear()
    hf.capacity.cache_clear()
    yield tmp_path, start, end
    hf.weather.cache_clear()
    hf.capacity.cache_clear()
