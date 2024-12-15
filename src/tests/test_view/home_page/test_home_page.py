
import pytest
from unittest.mock import Mock, patch
from flet import Text, Row, Container
from pw_view.home_page.home_page import HomePage
from flet.matplotlib_chart import MatplotlibChart

@pytest.fixture
def mock_view():
    """Mock the View object and its attributes."""
    mock = Mock()
    mock.background_image = Mock()
    mock.main_app = Mock()
    mock.main_app.update = Mock()
    mock.page_header_style = "Light"
    return mock

@pytest.fixture
def mock_data():
    """Mock HomePageData input."""
    return {
        "current_position": "2nd",
        "driver1": "John Doe",
        "driver1_contract": 3,
        "driver2": "Jane Smith",
        "driver2_contract": 2,
        "technical_director": "Dr. Who",
        "technical_director_contract": 4,
        "commercial_manager": "Mr. Moneybags",
        "commercial_manager_contract": 5,
        "next_race": "Australian GP",
        "next_race_week": 12,
        "team_average_stats": {
            "car_speed": 85,
            "driver_skill": 90,
            "managers": 80,
            "staff": 100,
            "facilities": 95,
            "sponsorship": 70,
            "max_staff": 100,
            "max_sponsorship": 100,
        },
        "player_car": 90,
        "player_drivers": 85,
        "player_managers": 75,
        "player_staff": 95,
        "player_facilities": 88,
        "player_sponsorship": 60,
    }

def test_update_page(mock_view, mock_data):
    """Test the update_page method."""
    homepage = HomePage(mock_view)
    homepage.update_page(mock_data)

    assert homepage.current_team_pos_text.value == "Current Position: 2nd"
    assert homepage.driver1_text.value == "Driver 1: John Doe - Contract: 3 Year(s)"
    assert homepage.driver2_text.value == "Driver 2: Jane Smith - Contract: 2 Year(s)"
    assert homepage.technical_director_text.value == "Technical Director: Dr. Who - Contract: 4 Year(s)"
    assert homepage.commercial_manager_text.value == "Commercial Manager: Mr. Moneybags - Contract: 5 Year(s)"
    assert homepage.next_race_text.value == "Next Race: Australian GP"
    assert homepage.next_race_week_text.value == "Week: 12"

def test_update_plot(mock_view, mock_data):
    """Test the update_plot method."""
    homepage = HomePage(mock_view)

    # Create a mock scatter return value that behaves like a real scatter plot
    mock_scatter_handle = Mock()

    with patch.object(homepage.axs, "bar") as mock_bar, \
         patch.object(homepage.axs, "scatter", return_value=mock_scatter_handle) as mock_scatter, \
         patch.object(homepage.axs, "legend") as mock_legend, \
         patch.object(homepage.fig, "subplots_adjust") as mock_adjust:
        
        homepage.update_plot(mock_data)

        # Validate bar chart data
        categories = ["Car", "Drivers", "Managers", "Staff", "Facilities", "Sponsors"]
        player_values = [90, 85, 75, 95, 88, 60]
        mock_bar.assert_any_call(categories, player_values, bottom=0, width=0.2, align="edge", color="#A0CAFD")

        # Validate scatter calls and ensure a mock object is returned for the legend
        assert mock_scatter.call_count == len(categories)  # One call per category
        mock_legend.assert_called_once()
        mock_adjust.assert_called_with(left=0.07, right=0.97, top=0.90, bottom=0.15)