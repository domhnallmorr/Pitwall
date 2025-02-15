import pytest
from unittest.mock import Mock
from unittest.mock import patch

import flet as ft
from pw_view.main_window import MainWindow
from pw_view.view_enums import ViewPageEnums

@pytest.fixture
def mock_view():
    """Fixture to mock the View object."""
    view = Mock()
    view.home_page = ft.Container()
    view.email_page = ft.Container()
    view.standings_page = ft.Container()
    view.calendar_page = ft.Container()
    view.staff_page = ft.Container()
    view.hire_staff_page = ft.Container()
    view.grid_page = ft.Container()
    view.finance_page = ft.Container()
    view.car_page = ft.Container()
    view.facility_page = ft.Container()
    view.upgrade_facility_page = ft.Container()
    view.main_app = Mock()
    return view

@pytest.fixture
def main_window(mock_view):
    """Fixture to create a MainWindow instance."""
    return MainWindow(mock_view)

def test_initialization(main_window):
    """Test that MainWindow initializes correctly."""
    assert main_window.header is not None
    assert main_window.content_row is not None
    assert main_window.nav_sidebar is not None

def test_change_page(main_window, mock_view):
    """Test the change_page method."""
    main_window.change_page(ViewPageEnums.EMAIL)
    assert isinstance(main_window.content_row.controls[1], ft.Container)  # Should be email_page
    assert main_window.content_row.controls[1] == mock_view.email_page

    main_window.change_page(ViewPageEnums.HOME)
    assert main_window.content_row.controls[1] == mock_view.home_page

def test_update_window(main_window, mock_view):
    """Test the update_window method."""
    with patch.object(main_window.week_text, "update") as mock_update:
        main_window.update_window("Test Team", "Week 2 - 1999", True)
        assert main_window.team_text.value == "Test Team"
        assert main_window.week_text.value == "Week 2 - 1999"
        mock_update.assert_called_once()


def test_update_email_button(main_window):
    """Test the update_email_button method."""
    main_window.update_email_button(5)
    assert main_window.nav_sidebar.email_btn.text == "Email (5)"

    main_window.update_email_button(0)
    assert main_window.nav_sidebar.email_btn.text == "Email"
