import pytest
import pandas as pd
import flet as ft
from unittest.mock import MagicMock
from pw_view.calendar_page.calendar_page import CalendarPage

@pytest.fixture
def mock_view():
    """Mock the View class required by CalendarPage."""
    mock = MagicMock()
    mock.page_header_style = "headline"
    mock.background_image = ft.Container(content=ft.Text("Background"))
    mock.main_app.update = MagicMock()
    return mock

@pytest.fixture
def f1_schedule_short():
    """Provide a shortened F1 schedule DataFrame."""
    return pd.DataFrame({
        "Week": [10, 13, 15],
        "Track": ["Albert Park", "Interlagos", "Autodromo Enzo e Dino Ferrari"],
        "Country": ["Australia", "Brazil", "Italy"],
        "Location": ["Melbourne", "Sao Paulo", "Imola"]
    })

def test_update_page_f1_schedule_short(mock_view, f1_schedule_short):
    """Test the update_page method with a shortened F1 schedule."""
    calendar_page = CalendarPage(view=mock_view)

    # Invoke the method
    
    calendar_page.update_page(f1_schedule_short)

    # Check if the controls are updated correctly
    assert len(calendar_page.controls) == 2  # Header + background stack
    assert isinstance(calendar_page.background_stack, ft.Stack)

    # Verify the table creation
    assert hasattr(calendar_page, "calendar_table")
    table = calendar_page.calendar_table
    assert isinstance(table, ft.DataTable)
    assert len(table.columns) == f1_schedule_short.shape[1]
    assert len(table.rows) == len(f1_schedule_short)  # Rows match the data

    # Verify the column headers
    column_headers = ["#", "Week", "Track", "Country", "Location"]
    for idx, header in enumerate(column_headers):
        assert table.columns[idx].label.content.value == header

    # Verify the first row content matches the DataFrame
    first_row = table.rows[0]
    assert first_row.cells[1].content.value == 10  # Week
    assert first_row.cells[2].content.value == "Albert Park"  # Track
    assert first_row.cells[3].content.value == "Australia"  # Country
    assert first_row.cells[4].content.value == "Melbourne"  # Location

    # Ensure the view's main_app.update was called
    mock_view.main_app.update.assert_called_once()
