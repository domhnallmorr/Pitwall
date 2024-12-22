import pytest
from unittest.mock import Mock, patch
import flet as ft
from pw_view.staff_page.staff_page import StaffPage
from pw_model.pw_model_enums import StaffRoles

@pytest.fixture
def mock_view():
    """Fixture to mock the view object."""
    view = Mock()
    view.clicked_button_style = {"bgcolor": "blue"}
    view.page_header_style = "title"
    view.background_image = Mock()
    view.main_app = Mock()
    view.controller = Mock()
    return view

def test_staff_page_initialization(mock_view):
    """Test StaffPage initialization."""
    page = StaffPage(view=mock_view)

    assert isinstance(page.buttons_row, ft.Row)
    assert len(page.staff_replace_buttons) == 4
    assert isinstance(page.driver_row, ft.Row)
    assert page.driver_containers, "Driver containers should be initialized"

def test_display_drivers(mock_view):
	"""Test the display_drivers method."""
	page = StaffPage(view=mock_view)
	page.display_drivers(Mock())

	assert page.drivers_btn.style == mock_view.clicked_button_style
	assert page.driver_row in page.background_stack.controls[1].controls
    
def test_display_managers(mock_view):
    """Test the display_managers method."""
    page = StaffPage(view=mock_view)
    page.display_managers(Mock())

    assert page.manager_button.style == mock_view.clicked_button_style
    assert page.manager_row in page.background_stack.controls[1].controls

def test_replace_driver(mock_view):
    """Test replace_driver triggers controller call."""
    page = StaffPage(view=mock_view)
    mock_event = Mock()
    mock_event.control.data = StaffRoles.DRIVER1

    page.replace_driver(mock_event)
    page.view.controller.staff_hire_controller.launch_replace_staff.assert_called_once_with(StaffRoles.DRIVER1)

def test_update_page(mock_view):
    """Test update_page method updates text values."""
    page = StaffPage(view=mock_view)
    data = {
        "driver1": "Max Verstappen",
        "driver2": "Lewis Hamilton",
        "driver1_age": 26,
        "driver2_age": 38,
        "driver1_country": "Netherlands",
        "driver2_country": "UK",
        "driver1_speed": 90,
        "driver2_speed": 88,
        "driver1_salary": 5000000,
        "driver2_salary": 7000000,
        "driver1_contract_length": 3,
        "driver2_contract_length": 2,
        "driver1_retiring": False,
        "driver2_retiring": False,
        "player_requiring_driver1": True,
        "player_requiring_driver2": False,
        "technical_director": "Adrian Newey",
        "technical_director_age": 64,
        "technical_director_contract_length": 5,
        "technical_director_skill": 95,
        "player_requiring_technical_director": True,
        "commercial_manager": "Toto Wolff",
        "commercial_manager_age": 52,
        "commercial_manager_contract_length": 4,
        "commercial_manager_skill": 85,
        "player_requiring_commercial_manager": True,
        "staff_values": [("Team A", 50), ("Team B", 80)],
    }

    page.update_page(data)

    # Validate driver details
    assert page.driver_name_texts[0].value == "Name: Max Verstappen"
    assert page.driver_name_texts[1].value == "Name: Lewis Hamilton"

    assert page.driver_age_texts[0].value == "Age: 26 Years"
    assert page.driver_age_texts[1].value == "Age: 38 Years"

    assert page.driver_country_texts[0].value == "Country: Netherlands"
    assert page.driver_country_texts[1].value == "Country: UK"

    # Verify salary and contract
    assert page.driver_salary_texts[0].value == "Salary: $5,000,000"
    assert page.driver_contract_length_texts[1].value == "Contract Length: 2 Years"

    # Check if replace buttons are correctly enabled/disabled
    assert not page.staff_replace_buttons[0].disabled
    assert page.staff_replace_buttons[1].disabled
