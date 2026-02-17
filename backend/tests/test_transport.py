import random

from app.core.transport import TransportManager, TransportCosts


def test_calculate_cost_uses_country_tier():
    manager = TransportManager(volatility=0.0)
    base_cost, applied_cost = manager.calculate_cost("Japan", rng=random.Random(1))
    assert base_cost == TransportCosts.MAX
    assert applied_cost == TransportCosts.MAX


def test_calculate_cost_defaults_to_medium_for_unknown_country():
    manager = TransportManager(volatility=0.0)
    base_cost, applied_cost = manager.calculate_cost("Unknownland", rng=random.Random(2))
    assert base_cost == TransportCosts.MEDIUM
    assert applied_cost == TransportCosts.MEDIUM


def test_calculate_cost_applies_volatility_bounds():
    manager = TransportManager(volatility=0.15)
    base_cost, applied_cost = manager.calculate_cost("France", rng=random.Random(3))
    lower = int(round(base_cost * 0.85))
    upper = int(round(base_cost * 1.15))
    assert lower <= applied_cost <= upper
