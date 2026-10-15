"""Strategy B and the legs its PnL is broken down into.

A           the engine's positions (de-power-spread): long and short, 10 MW per quarter hour
B           A with every short set to zero (the strategy of this repo)
A_short     A's short positions only, so A = B + A_short
always_long +1 in every quarter hour: the unconditional long premium of the spread
"""
from __future__ import annotations

import numpy as np

LEGS = ("B", "A", "A_short", "always_long")


def long_only(side_a) -> np.ndarray:
    """B: the engine's positions without the shorts."""
    side_a = np.asarray(side_a, dtype="float64")
    return np.where(side_a > 0, side_a, 0.0)


def legs(side_a) -> dict[str, np.ndarray]:
    side_a = np.asarray(side_a, dtype="float64")
    return {"B": long_only(side_a), "A": side_a, "A_short": np.where(side_a < 0, side_a, 0.0),
            "always_long": np.ones_like(side_a)}
