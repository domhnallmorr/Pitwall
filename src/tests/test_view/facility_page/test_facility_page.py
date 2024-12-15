
import pytest
from unittest.mock import MagicMock
import flet as ft
from pw_view.facility_page.facility_page import FacilityPage

@pytest.fixture
def mock_view():
    view = MagicMock()
    view.page_header_style = "header-style"
    view.background_image = ft.Container()
    view.main_app.update = MagicMock()
    view.controller.facilities_controller.clicked_update_facilities = MagicMock()
    return view

@pytest.fixture
def facility_page(mock_view):
    return FacilityPage(view=mock_view)

def test_initialization(facility_page, mock_view):
    assert isinstance(facility_page, ft.Column)
    assert len(facility_page.controls) == 1
    assert facility_page.controls[0].value == "Facilities"
    assert facility_page.controls[0].theme_style == mock_view.page_header_style

def test_setup_widgets(facility_page):
    facility_page.setup_widgets()
    assert isinstance(facility_page.buttons_row, ft.Row)
    assert len(facility_page.buttons_row.controls) == 1
    assert isinstance(facility_page.buttons_container, ft.Container)

def test_update_page(facility_page, mock_view):
    mock_data = {
        "facility_values": [
            ["Team A", 70],
            ["Team B", 50]
        ]
    }
    
    facility_page.update_page(mock_data)

    assert isinstance(facility_page.background_stack, ft.Stack)
    assert len(facility_page.background_stack.controls) == 2

    facility_rows = facility_page.setup_facilities_progress_bars(mock_data)
    assert len(facility_rows) == 2
    assert facility_rows[0].controls[0].value == "Team A:"
    assert isinstance(facility_rows[0].controls[1].content, ft.ProgressBar)

    assert facility_page.controls[1] == facility_page.background_stack
    mock_view.main_app.update.assert_called_once()

def test_update_facilities_action(facility_page, mock_view):
    event = MagicMock()
    facility_page.update_facilities(event)
    mock_view.controller.facilities_controller.clicked_update_facilities.assert_called_once()

def test_enable_disable_upgrade_button(facility_page, mock_view):
    facility_page.disable_upgrade_button()
    assert facility_page.update_button.disabled is True
    mock_view.main_app.update.assert_called_once()

    facility_page.enable_upgrade_button()
    assert facility_page.update_button.disabled is False
    assert mock_view.main_app.update.call_count == 2
