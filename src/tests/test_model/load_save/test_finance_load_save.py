import sqlite3
import pytest
import pandas as pd
from unittest.mock import MagicMock

from pw_model.load_save.finance_load_save import save_finance_model, load_finance_model

@pytest.fixture
def mock_model():
    """Create a mock model with financial attributes."""
    mock_finance = MagicMock()
    mock_finance.season_opening_balance = 500000
    mock_finance.consecutive_weeks_in_debt = 3

    mock_team = MagicMock()
    mock_team.finance_model = mock_finance

    mock_model = MagicMock()
    mock_model.player_team_model = mock_team

    return mock_model

@pytest.fixture
def db_connection():
    """Provide an in-memory SQLite database."""
    conn = sqlite3.connect(":memory:")
    yield conn
    conn.close()

def test_save_and_load_finance_model(mock_model, db_connection):
    """Test saving and loading the finance model."""
    # Mock the external functions to return expected values
    from pw_model.team.team_facade import get_season_opening_balance, get_weeks_in_debt
    get_season_opening_balance.return_value = 500000
    get_weeks_in_debt.return_value = 3

    # Save data to the in-memory database
    save_finance_model(mock_model, db_connection)

    # Load data back into the model
    load_finance_model(mock_model, db_connection)

    # Verify that the loaded data matches what was saved
    assert mock_model.player_team_model.finance_model.season_opening_balance == 500000
    assert mock_model.player_team_model.finance_model.consecutive_weeks_in_debt == 3
