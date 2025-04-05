import pytest
from unittest.mock import MagicMock
from pw_model.driver_negotiation.driver_salary_expectations import determine_driver_salary_expectation

@pytest.mark.parametrize(
    "rating, starts, age, current_salary, expected_salary",
    [
        # ELITE classification test cases
        # rating >= 90, starts >= 40 => classification cap = 29,000,000
        # Age < 25 => +10% salary; Age < 32 => +20%; Else => +0%
        (95, 50, 24, 25_000_000, 27_500_000),  # 25M * 1.1 = 27.5M < 29M
        (95, 50, 25, 28_000_000, 29_000_000),  # 28M * 1.2 = 33.6M => capped at 29M

        # TOP classification test cases
        # rating >= 70, starts >= 30 => classification cap = 14,000,000
        (80, 31, 28, 12_000_000, 14_000_000),  # 12M * 1.2 = 14.4M => capped at 14M
        (80, 31, 32, 12_000_000, 12_000_000),  # 12M * 1.0 = 12M < 14M => no cap

        # MID classification test cases
        # rating >= 50, starts >= 16 => classification cap = 6,000,000
        (60, 16, 24, 5_000_000, 5_500_000),    # 5M * 1.1 = 5.5M < 6M => no cap
        (60, 16, 40, 7_000_000, 6_000_000),    # 7M * 1.0 = 7M => capped at 6M

        # BOTTOM classification test cases
        # (anything else) => classification cap = 1,600,000
        (40, 5, 24, 1_500_000, 1_600_000),     # 1.5M * 1.1 = 1.65M => capped at 1.6M
        (40, 5, 35, 1_000_000, 1_000_000),     # 1M * 1.0 = 1M < 1.6M => no cap
    ],
)
def test_determine_driver_salary_expectation(rating, starts, age, current_salary, expected_salary):
    # Mock the driver_model returned by model.get_driver_model
    mock_driver_model = MagicMock()
    mock_driver_model.overall_rating = rating
    mock_driver_model.career_stats.starts = starts
    mock_driver_model.age = age
    mock_driver_model.contract.salary = current_salary

    # Mock the main model
    mock_model = MagicMock()
    mock_model.get_driver_model.return_value = mock_driver_model

    # Call the function under test
    actual_salary = determine_driver_salary_expectation(mock_model, "mock_driver")

    # Compare the result to our expectation
    assert actual_salary == expected_salary, (
        f"For rating={rating}, starts={starts}, age={age}, "
        f"and current_salary={current_salary}, expected {expected_salary} "
        f"but got {actual_salary}"
    )
