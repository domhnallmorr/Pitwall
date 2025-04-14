import pytest
import sqlite3
from unittest.mock import MagicMock, patch
from pw_model.finance.transport_costs import (
    TransportCostsModel,
    TransportCostsRandomiser,
    TransportCosts,
)
from pw_model.load_save.transport_costs_load_save import save_transport_costs_model, load_transport_costs

# Mock Model for testing
class MockModel:
    class MockSeason:
        def __init__(self):
            self.calendar = MagicMock()
            self.calendar.countries = ["Australia", "Spain", "Japan"]
            self.calendar.current_track_model = MagicMock()
            self.calendar.current_track_model.country = "Australia"

    class MockGameData:
        def __init__(self):
            self._current_track_country = "Australia"
            
        def current_track_country(self):
            return self._current_track_country
        
    def __init__(self):
        self.season = self.MockSeason()
        self.game_data = self.MockGameData()        
        self.inbox = MagicMock()

@pytest.fixture
def transport_costs_model():
    mock_model = MockModel()
    return TransportCostsModel(mock_model)

@pytest.fixture
def mock_db_connection():
    return sqlite3.connect(":memory:")

def test_save_and_load_transport_costs_model(transport_costs_model, mock_db_connection):
    # Set up some mock data
    transport_costs_model.setup_new_season()
    transport_costs_model.gen_race_transport_cost()
    transport_costs_model.gen_race_transport_cost()

    save_transport_costs_model(transport_costs_model, mock_db_connection)

    # Create a new instance to test loading
    new_transport_costs_model = TransportCostsModel(MockModel())
    load_transport_costs(mock_db_connection, new_transport_costs_model)

    assert new_transport_costs_model.estimated_season_costs == transport_costs_model.estimated_season_costs
    assert new_transport_costs_model.total_costs == transport_costs_model.total_costs
    assert new_transport_costs_model.costs_by_race == transport_costs_model.costs_by_race