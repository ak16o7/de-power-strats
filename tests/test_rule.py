import numpy as np

from strats import rule


def test_long_only_drops_every_short_and_nothing_else():
    a = np.array([1, -1, 0, 1, -1, 0.5, -0.5])
    b = rule.long_only(a)
    assert (b >= 0).all()
    assert np.array_equal(b[a > 0], a[a > 0])
    assert (b[a <= 0] == 0).all()


def test_legs_add_up():
    a = np.array([1, -1, 0, 1, -1])
    lg = rule.legs(a)
    assert np.array_equal(lg["A"], lg["B"] + lg["A_short"])
    assert (lg["always_long"] == 1).all() and set(lg) == set(rule.LEGS)
