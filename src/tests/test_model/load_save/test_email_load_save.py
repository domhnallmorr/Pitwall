import pytest
import sqlite3
import pandas as pd
from pw_model.load_save.email_load_save import save_email, load_email
from pw_model.email.email_model import Inbox, EmailStatusEnums

# Mock Model class for testing
class MockModel:
    def __init__(self):
        self.inbox = Inbox(self)

def test_save_and_load_email():
    # Setup: Create a mock model and add emails
    model = MockModel()
    model.inbox.add_email("Test Message 1", "Test Subject 1", "Sender 1")
    model.inbox.add_email("Test Message 2", "Test Subject 2", "Sender 2", status=EmailStatusEnums.READ)
    
    # Use an in-memory SQLite database
    conn = sqlite3.connect(":memory:")
    
    # Act: Save emails to the database
    save_email(model, conn)
    
    # Create a new mock model to load into
    new_model = MockModel()
    
    # Act: Load emails from the database
    load_email(conn, new_model)
    
    # Get DataFrames for comparison
    original_df = model.inbox.generate_dataframe()
    loaded_df = new_model.inbox.generate_dataframe()
    
    # Assert that the data is correctly loaded
    pd.testing.assert_frame_equal(original_df, loaded_df)
    
    # Cleanup
    conn.close()

if __name__ == "__main__":
    pytest.main()
