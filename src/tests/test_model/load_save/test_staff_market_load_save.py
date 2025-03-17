import pytest
import sqlite3
import pandas as pd
from unittest.mock import Mock, patch
from pw_model.pw_model_enums import StaffRoles

# Import the module we're testing
from pw_model.load_save import staff_market_load_save


@pytest.fixture
def mock_model():
    """Create a mock model with staff_market attribute containing required DataFrames."""
    model = Mock()
    model.staff_market = Mock()
    
    # Create test DataFrames with realistic sample data
    # Grid this year
    this_year_data = [
        ["Williams", "Frank Williams", "Jacques Villeneuve", "Heinz-Harald Frentzen", "Patrick Head", "John Smith"],
        ["Ferrari", "Jean Todt", "Michael Schumacher", "Eddie Irvine", "Ross Brawn", "Jane Doe"]
    ]
    columns = ["team", StaffRoles.TEAM_PRINCIPAL.value, StaffRoles.DRIVER1.value, 
               StaffRoles.DRIVER2.value, StaffRoles.TECHNICAL_DIRECTOR.value, 
               StaffRoles.COMMERCIAL_MANAGER.value]
    
    model.staff_market.grid_this_year_df = pd.DataFrame(columns=columns, data=this_year_data)

    # Grid next year
    next_year_data = [
        ["Williams", "Frank Williams", "Jacques Villeneuve", None, "Patrick Head", "John Smith"],
        ["Ferrari", "Jean Todt", "Michael Schumacher", "Eddie Irvine", None, "Jane Doe"]
    ]
    model.staff_market.grid_next_year_df = pd.DataFrame(columns=columns, data=next_year_data)
    model.staff_market.grid_next_year_announced_df = pd.DataFrame(columns=columns, data=next_year_data)

    # New contracts
    contract_columns = ["Team", "WeekToAnnounce", "DriverIdx", "Driver", "Salary", "ContractLength"]
    contract_data = [
        ["Williams", 10, StaffRoles.DRIVER2.value, "Damon Hill", 4000000, 3],
        ["Ferrari", 15, StaffRoles.TECHNICAL_DIRECTOR.value, "Adrian Newey", 5000000, 4]
    ]
    model.staff_market.new_contracts_df = pd.DataFrame(columns=contract_columns, data=contract_data)
    
    return model


@pytest.fixture
def temp_db():
    """Create an in-memory SQLite database for testing."""
    conn = sqlite3.connect(":memory:")
    yield conn
    conn.close()


class TestStaffMarketLoadSave:
    def test_save_grid_this_year(self, mock_model, temp_db):
        # Call the function to test
        staff_market_load_save.save_grid_this_year(mock_model, temp_db)
        
        # Verify the data was saved correctly
        saved_df = pd.read_sql('SELECT * FROM grid_this_year_df', temp_db)
        pd.testing.assert_frame_equal(saved_df, mock_model.staff_market.grid_this_year_df)
    
    def test_save_grid_next_year(self, mock_model, temp_db):
        # Call the function to test
        staff_market_load_save.save_grid_next_year(mock_model, temp_db)
        
        # Verify the data was saved correctly
        saved_df = pd.read_sql('SELECT * FROM grid_next_year_df', temp_db)
        pd.testing.assert_frame_equal(saved_df, mock_model.staff_market.grid_next_year_df)
        
        saved_announced_df = pd.read_sql('SELECT * FROM grid_next_year_announced', temp_db)
        pd.testing.assert_frame_equal(saved_announced_df, mock_model.staff_market.grid_next_year_announced_df)
    
    def test_save_new_contracts_df(self, mock_model, temp_db):
        # Call the function to test
        staff_market_load_save.save_new_contracts_df(mock_model, temp_db)
        
        # Verify the data was saved correctly
        saved_df = pd.read_sql('SELECT * FROM new_contracts_df', temp_db)
        pd.testing.assert_frame_equal(saved_df, mock_model.staff_market.new_contracts_df)
    
    def test_load_grid_this_year(self, mock_model, temp_db):
        # Save data first
        staff_market_load_save.save_grid_this_year(mock_model, temp_db)
        
        # Clear the original DataFrame for testing
        original_df = mock_model.staff_market.grid_this_year_df.copy()
        mock_model.staff_market.grid_this_year_df = pd.DataFrame()
        
        # Call the function to test
        staff_market_load_save.load_grid_this_year(temp_db, mock_model)
        
        # Verify data was loaded correctly
        pd.testing.assert_frame_equal(mock_model.staff_market.grid_this_year_df, original_df)
    
    def test_load_grid_next_year(self, mock_model, temp_db):
        # Save data first
        staff_market_load_save.save_grid_next_year(mock_model, temp_db)
        staff_market_load_save.save_new_contracts_df(mock_model, temp_db)
        
        # Clear the original DataFrames for testing
        original_next_year_df = mock_model.staff_market.grid_next_year_df.copy()
        original_announced_df = mock_model.staff_market.grid_next_year_announced_df.copy()
        original_contracts_df = mock_model.staff_market.new_contracts_df.copy()
        
        mock_model.staff_market.grid_next_year_df = pd.DataFrame()
        mock_model.staff_market.grid_next_year_announced_df = pd.DataFrame()
        mock_model.staff_market.new_contracts_df = pd.DataFrame()
        
        # Call the function to test
        staff_market_load_save.load_grid_next_year(temp_db, mock_model)
        
        # Verify data was loaded correctly
        pd.testing.assert_frame_equal(mock_model.staff_market.grid_next_year_df, original_next_year_df)
        pd.testing.assert_frame_equal(mock_model.staff_market.grid_next_year_announced_df, original_announced_df)
        pd.testing.assert_frame_equal(mock_model.staff_market.new_contracts_df, original_contracts_df)