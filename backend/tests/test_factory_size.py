from app.core.factory_size import (
    get_factory_limits,
    infer_factory_size_from_overhead,
    normalize_factory_size,
)


def test_normalize_factory_size_clamps_to_valid_range():
    assert normalize_factory_size(None) == 1
    assert normalize_factory_size(0) == 1
    assert normalize_factory_size(-3) == 1
    assert normalize_factory_size(3) == 3
    assert normalize_factory_size(8) == 5


def test_get_factory_limits_returns_expected_values_for_size():
    assert get_factory_limits(1) == {
        "factory_size": 1,
        "workforce": 160,
        "commercial_staff": 40,
        "overhead": 1_600_000,
    }
    assert get_factory_limits(4) == {
        "factory_size": 4,
        "workforce": 320,
        "commercial_staff": 80,
        "overhead": 6_400_000,
    }


def test_get_factory_limits_normalizes_invalid_sizes():
    assert get_factory_limits(0)["factory_size"] == 1
    assert get_factory_limits(9)["factory_size"] == 5


def test_infer_factory_size_from_known_overhead_matches_exact_table():
    assert infer_factory_size_from_overhead(1_600_000) == 1
    assert infer_factory_size_from_overhead(3_200_000) == 2
    assert infer_factory_size_from_overhead(4_800_000) == 3
    assert infer_factory_size_from_overhead(6_400_000) == 4
    assert infer_factory_size_from_overhead(8_000_000) == 5


def test_infer_factory_size_from_overhead_rounds_up_to_next_band():
    assert infer_factory_size_from_overhead(None) == 1
    assert infer_factory_size_from_overhead(2_000_000) == 2
    assert infer_factory_size_from_overhead(5_000_000) == 4
    assert infer_factory_size_from_overhead(9_500_000) == 5
