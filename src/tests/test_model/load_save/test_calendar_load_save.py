import sqlite3
import pandas as pd
import pytest

from pw_model.load_save.calendar_load_save import save_calendar, load_calendar

# Dummy classes to mimic the structure of the actual Model
class DummyCalendar:
    def __init__(self, dataframe: pd.DataFrame):
        self.dataframe = dataframe

class DummySeason:
    def __init__(self, dataframe: pd.DataFrame):
        self.calendar = DummyCalendar(dataframe)

class DummyModel:
    def __init__(self, dataframe: pd.DataFrame):
        self.season = DummySeason(dataframe)

def test_save_and_load_calendar():
    # Create a sample DataFrame
    data = {
        "Week": [1, 2, 3],
        "Track": ["Track A", "Track B", "Track C"],
        "Country": ["Country A", "Country B", "Country C"],
        "Location": ["Location A", "Location B", "Location C"],
        "Winner": [None, None, None]
    }
    original_df = pd.DataFrame(data)
    
    # Initialize dummy model with the sample DataFrame
    model = DummyModel(original_df.copy())
    
    # Use an in-memory SQLite database
    conn = sqlite3.connect(":memory:")
    
    # Save the calendar to the SQLite database
    save_calendar(model, conn)
    
    # Clear the model's calendar DataFrame to simulate a fresh load
    model.season.calendar.dataframe = pd.DataFrame()
    
    # Load the calendar data back into the model
    load_calendar(conn, model)
    
    # Assert that the reloaded DataFrame matches the original DataFrame
    pd.testing.assert_frame_equal(model.season.calendar.dataframe, original_df)
    
    conn.close()

def test_load_without_saved_calendar():
    # Initialize a dummy model with an empty DataFrame
    model = DummyModel(pd.DataFrame())
    
    # Create an in-memory SQLite database without saving any calendar table
    conn = sqlite3.connect(":memory:")
    
    # Expect an error when trying to load from a non-existent table.
    # Note: pandas.read_sql wraps the sqlite3.OperationalError into pandas.errors.DatabaseError.
    with pytest.raises(pd.errors.DatabaseError) as exc_info:
        load_calendar(conn, model)
    
    # Optionally, check that the error message contains 'no such table'
    assert "no such table" in str(exc_info.value)
    
    conn.close()
