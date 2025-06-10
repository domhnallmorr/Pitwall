import sqlite3
import pytest
import pandas as pd
from unittest.mock import MagicMock

from pw_model.load_save.team_sponsors_load_save import save_team_sponsors, load_team_sponsors
from pw_model.load_save.sponsors_load_save import load_sponsors
from pw_model.pw_model_enums import SponsorTypes

@pytest.fixture
def mock_model():
    """Create a mock model with teams and sponsors."""
    # Mock sponsor model
    mock_sponsor = MagicMock()
    mock_sponsor.title_sponsor = "Some Sponsor"
    mock_sponsor.title_sponsor_value = "500000"
    mock_sponsor.other_sponsorship = 200000
    mock_sponsor.title_sponsor_contract_length = 3

    # Mock team model
    mock_team = MagicMock()
    mock_team.name = "RedBull Racing"
    mock_team.finance_model.sponsorship_model = mock_sponsor

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
    save_team_sponsors(mock_model, db_connection)

    # Load sponsors data
    sponsors_df = load_team_sponsors(db_connection)

    # Verify data integrity
    assert len(sponsors_df) == 1  # Only one team
    assert sponsors_df.iloc[0]["Team"] == "RedBull Racing"
    assert sponsors_df.iloc[0]["TitleSponsor"] == "Some Sponsor"
    assert sponsors_df.iloc[0]["TitleSponsorValue"] == 500000
    assert sponsors_df.iloc[0]["OtherSponsorsValue"] == 200000

def test_load_sponsors_from_roster(db_connection, mock_model):
    """Test loading sponsors from roster with correct contract assignments."""
    # Create test data for sponsors
    sponsors_data = [
        ("Shell", 1000000, 2, "Ferrari"),
        ("West", 800000, 3, "McLaren"),
        ("None", None, None, "Williams")  # Team without title sponsor
    ]
    
    # Create and populate the TeamSponsors table
    db_connection.execute('''
        CREATE TABLE IF NOT EXISTS TeamSponsors (
            Team TEXT,
            TitleSponsor TEXT,
            TitleSponsorValue INTEGER,
            TitleSponsorContractLength INTEGER,
            OtherSponsorsValue INTEGER
        )
    ''')
    
    for sponsor_name, value, length, team in sponsors_data:
        db_connection.execute('''
            INSERT INTO TeamSponsors (
                Team, 
                TitleSponsor, 
                TitleSponsorValue, 
                TitleSponsorContractLength, 
                OtherSponsorsValue
            ) VALUES (?, ?, ?, ?, ?)
        ''', (team, sponsor_name if sponsor_name != "None" else None, value, length, 200000))

    # Create and populate the Sponsors table
    db_connection.execute('''
        CREATE TABLE IF NOT EXISTS Sponsors (
            Name TEXT,
            Year TEXT,
            Wealth INTEGER
        )
    ''')
    
    # Add sponsors to roster (using 'default' year for current sponsors)
    for sponsor_name, _, _, _ in sponsors_data:
        if sponsor_name != "None":
            db_connection.execute('INSERT INTO Sponsors (Name, Year, Wealth) VALUES (?, ?, ?)',
                               (sponsor_name, 'default', 70))

    # Load sponsors using the function
    load_sponsors(db_connection, mock_model)

    # Verify the loaded sponsors
    assert len(mock_model.sponsors) == 2  # Should have 2 sponsors (Shell and West)
    assert len(mock_model.future_sponsors) == 0  # No future sponsors in this test

    # Check specific sponsor details
    shell_sponsor = next(s for s in mock_model.sponsors if s.name == "Shell")
    west_sponsor = next(s for s in mock_model.sponsors if s.name == "West")

    # Verify Shell sponsor details
    assert shell_sponsor.name == "Shell"
    assert shell_sponsor.contract.total_payment == 1000000
    assert shell_sponsor.contract.contract_length == 2
    assert shell_sponsor.contract.sponsor_type == SponsorTypes.TITLE

    # Verify West sponsor details
    assert west_sponsor.name == "West"
    assert west_sponsor.contract.total_payment == 800000
    assert west_sponsor.contract.contract_length == 3
    assert west_sponsor.contract.sponsor_type == SponsorTypes.TITLE
