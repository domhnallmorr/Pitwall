import pytest
from unittest.mock import MagicMock
from pw_model.driver_negotiation.driver_negotiation_enums import DriverCategory
from pw_model.driver_negotiation.driver_classification import classify_driver

@pytest.mark.parametrize(
    "rating, starts, expected_category",
    [
        # ELITE -> rating >= 90 and starts >= 40
        (90, 40, DriverCategory.ELITE),
        (95, 50, DriverCategory.ELITE),

        # TOP -> rating >= 70 and starts >= 30 (but less than ELITE criteria)
        (70, 30, DriverCategory.TOP),
        (89, 39, DriverCategory.TOP),

        # MID -> rating >= 50 and starts >= 16 (but less than TOP criteria)
        (50, 16, DriverCategory.MID),
        (69, 29, DriverCategory.MID),

        # BOTTOM -> everything else
        (49, 16, DriverCategory.BOTTOM),
        (80, 15, DriverCategory.BOTTOM),
        (10, 100, DriverCategory.BOTTOM),
    ],
)
def test_classify_driver(rating, starts, expected_category):
    # Mock DriverModel
    mock_driver_model = MagicMock()
    mock_driver_model.overall_rating = rating
    mock_driver_model.career_stats.starts = starts

    # Mock Model that returns our mock DriverModel
    mock_model = MagicMock()
    mock_entity_manager = MagicMock()
    mock_entity_manager.get_driver_model.return_value = mock_driver_model
    mock_model.entity_manager = mock_entity_manager

    # Call the function under test
    category = classify_driver("mock_driver_name", mock_model)

    # Assert
    assert category == expected_category, (
        f"For rating={rating} and starts={starts}, "
        f"expected {expected_category} but got {category}"
    )
