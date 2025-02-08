import sqlite3
import pytest
import pandas as pd
from unittest.mock import MagicMock

from pw_model.load_save.standings_load_save import save_standings, load_standings

@pytest.fixture
def mock_model():
    """Create a mock model with championship standings."""
    # Mock drivers standings DataFrame
    drivers_standings_df = pd.DataFrame({
        "Driver": ["Max Verstappen", "Lewis Hamilton"],
        "Points": [300, 280]
    })

    # Mock constructors standings DataFrame
    constructors_standings_df = pd.DataFrame({
        "Team": ["Red Bull", "Mercedes"],
        "Points": [500, 450]
    })

    # Mock standings manager
    mock_standings_manager = MagicMock()
    mock_standings_manager.drivers_standings_df = drivers_standings_df
    mock_standings_manager.constructors_standings_df = constructors_standings_df

    # Mock season
    mock_season = MagicMock()
    mock_season.standings_manager = mock_standings_manager

    # Mock overall game model
    mock_model = MagicMock()
    mock_model.season = mock_season

    return mock_model

@pytest.fixture
def db_connection():
    """Provide an in-memory SQLite database."""
    conn = sqlite3.connect(":memory:")
    yield conn
    conn.close()

def test_save_and_load_standings(mock_model, db_connection):
    """Test saving and loading championship standings."""
    # Save standings data
    save_standings(mock_model, db_connection)

    # Create a new mock model to load data into
    new_mock_model = MagicMock()
    new_mock_model.season = MagicMock()
    new_mock_model.season.standings_manager = MagicMock()

    # Load standings data into the new model
    load_standings(db_connection, new_mock_model)

    # Verify that the loaded data matches what was saved
    pd.testing.assert_frame_equal(
        new_mock_model.season.standings_manager.drivers_standings_df,
        mock_model.season.standings_manager.drivers_standings_df
    )

    pd.testing.assert_frame_equal(
        new_mock_model.season.standings_manager.constructors_standings_df,
        mock_model.season.standings_manager.constructors_standings_df
    )
