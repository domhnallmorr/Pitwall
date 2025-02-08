import sqlite3
import pytest
import pandas as pd
from unittest.mock import MagicMock

from pw_model.load_save.sponsors_load_save import save_sponsor_model, load_sponsors

@pytest.fixture
def mock_model():
    """Create a mock model with teams and sponsors."""
    # Mock sponsor model
    mock_sponsor = MagicMock()
    mock_sponsor.title_sponsor = 1
    mock_sponsor.title_sponsor_value = "500000"
    mock_sponsor.other_sponsorship = 200000

    # Mock team model
    mock_team = MagicMock()
    mock_team.name = "RedBull Racing"
    mock_team.finance_model.sponsors_model = mock_sponsor

    # Mock overall game model
    mock_model = MagicMock()
    mock_model.teams = [mock_team]

    return mock_model

@pytest.fixture
def db_connection():
    """Provide an in-memory SQLite database."""
    conn = sqlite3.connect(":memory:")
    yield conn
    conn.close()

def test_save_and_load_sponsors(mock_model, db_connection):
    """Test saving and loading sponsor data."""
    # Save sponsors data
    save_sponsor_model(mock_model, db_connection)

    # Load sponsors data
    sponsors_df = load_sponsors(db_connection)

    # Verify data integrity
    assert len(sponsors_df) == 1  # Only one team
    assert sponsors_df.iloc[0]["Team"] == "RedBull Racing"
    assert sponsors_df.iloc[0]["TitleSponsor"] == 1
    assert sponsors_df.iloc[0]["TitleSponsorValue"] == "500000"
    assert sponsors_df.iloc[0]["OtherSponsorsValue"] == 200000
