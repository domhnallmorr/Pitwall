import pytest
import sqlite3
from unittest.mock import MagicMock, patch
from pw_model.finance.transport_costs import (
    TransportCostsModel,
    TransportCostsRandomiser,
    TransportCosts,
)
# Mock Model for testing
class MockModel:
    class MockSeason:
        def __init__(self):
            self.calendar = MagicMock()
            self.calendar.countries = ["Australia", "Spain", "Japan"]
            self.calendar.current_track_model = MagicMock()
            self.calendar.current_track_model.country = "Australia"

    def __init__(self):
        self.season = self.MockSeason()
        self.inbox = MagicMock()

@pytest.fixture
def transport_costs_model():
    mock_model = MockModel()
    return TransportCostsModel(mock_model)

@pytest.fixture
def mock_db_connection():
    return sqlite3.connect(":memory:")

def test_setup_new_season(transport_costs_model):
    transport_costs_model.setup_new_season()
    assert transport_costs_model.estimated_season_costs > 0
    assert transport_costs_model.total_costs == 0
    assert transport_costs_model.costs_by_race == []

def test_gen_race_transport_cost(transport_costs_model):
    transport_costs_model.setup_new_season()
    transport_costs_model.gen_race_transport_cost()
    assert transport_costs_model.total_costs > 0
    assert len(transport_costs_model.costs_by_race) == 1
    assert transport_costs_model.costs_by_race[0] > 0

def test_randomiser():
    randomiser = TransportCostsRandomiser()
    for _ in range(100):  # Test randomness multiple times
        random_value = randomiser.gen_random_element_of_transport_cost()
        assert -30_000 <= random_value <= 80_000

def test_get_country_costs(transport_costs_model):
    assert transport_costs_model.get_country_costs("Australia") == TransportCosts.MAX.value
    assert transport_costs_model.get_country_costs("Spain") == TransportCosts.MEDIUM.value
    assert transport_costs_model.get_country_costs("Unknown Country") == TransportCosts.MEDIUM.value

def test_gen_race_transport_cost_with_multiple_races_and_mock_randomiser(transport_costs_model):
    # Mock the randomizer to return a specific value
    with patch.object(transport_costs_model.randomiser, 'gen_random_element_of_transport_cost', return_value=50_000):
        transport_costs_model.setup_new_season()

        # First race (Australia)
        transport_costs_model.gen_race_transport_cost()
        country1 = transport_costs_model.model.season.calendar.current_track_model.country
        expected_cost1 = transport_costs_model.get_country_costs(country1) + 50_000
        assert transport_costs_model.total_costs == expected_cost1
        assert transport_costs_model.costs_by_race == [expected_cost1]

        # Set up second race (Spain)
        transport_costs_model.model.season.calendar.current_track_model.country = "Spain"
        transport_costs_model.gen_race_transport_cost()
        country2 = transport_costs_model.model.season.calendar.current_track_model.country
        expected_cost2 = transport_costs_model.get_country_costs(country2) + 50_000
        assert transport_costs_model.total_costs == expected_cost1 + expected_cost2
        assert transport_costs_model.costs_by_race == [expected_cost1, expected_cost2]

def test_estimate_season_transport_costs_with_mock_randomiser(transport_costs_model):
    # Mock the randomizer to return a specific value
    with patch.object(transport_costs_model.randomiser, 'gen_random_element_of_transport_cost', return_value=50_000):
        # Ensure a controlled calendar with specific countries
        transport_costs_model.model.season.calendar.countries = ["Australia", "Spain", "Japan"]
        
        transport_costs_model.estimate_season_transport_costs()

        # Calculate expected season costs
        expected_costs = (
            transport_costs_model.get_country_costs("Australia") +
            transport_costs_model.get_country_costs("Spain") +
            transport_costs_model.get_country_costs("Japan")
        )
        assert transport_costs_model.estimated_season_costs == expected_costs