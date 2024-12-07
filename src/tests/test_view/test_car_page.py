import pytest
from unittest.mock import Mock, create_autospec
import flet as ft
from pw_view.car_page.car_page import CarPage


@pytest.fixture
def mock_view():
    # Create a mock view object with necessary attributes
    view = Mock()
    view.page_header_style = "titleLarge"
    view.background_image = ft.Container()
    view.main_app = Mock()
    return view


def test_car_page_initialization(mock_view):
    # Create an instance of CarPage
    car_page = CarPage(mock_view)

    # Assert initial contents
    assert len(car_page.controls) == 1
    assert isinstance(car_page.controls[0], ft.Text)
    assert car_page.controls[0].value == "Car"


def test_car_page_update_page(mock_view):
    # Mock data
    car_speeds = [("Car A", 50), ("Car B", 80)]

    # Create an instance of CarPage
    car_page = CarPage(mock_view)

    # Call update_page with mocked car speeds
    car_page.update_page(car_speeds)

    # Assert controls have been updated
    assert len(car_page.controls) == 2
    assert isinstance(car_page.controls[1], ft.Stack)

    # Check the background stack contains the correct elements
    stack_controls = car_page.controls[1].controls
    assert mock_view.background_image in stack_controls


def test_setup_car_speed_progress_bars(mock_view):
    # Mock data
    car_speeds = [("Car A", 50), ("Car B", 80)]

    # Create an instance of CarPage
    car_page = CarPage(mock_view)

    # Call setup_car_speed_progress_bars
    rows = car_page.setup_car_speed_progress_bars(car_speeds)

    # Assert the rows are created correctly
    assert len(rows) == len(car_speeds)
    for i, row in enumerate(rows):
        assert isinstance(row, ft.Row)
        assert len(row.controls) == 2
        assert isinstance(row.controls[0], ft.Text)
        assert row.controls[0].value == f"{car_speeds[i][0]}:"
        assert isinstance(row.controls[1], ft.Container)
        assert isinstance(row.controls[1].content, ft.ProgressBar)
        assert row.controls[1].content.value == car_speeds[i][1] / 100
