import pytest
import flet as ft

# Dummy classes to simulate the minimal view/controller/main_app environment
class DummyMainApp:
    def __init__(self):
        self.updated = False

    def update(self):
        self.updated = True

class DummyCarDevelopmentController:
    def __init__(self):
        self.selected = None

    def car_development_selected(self, data):
        self.selected = data

class DummyController:
    def __init__(self):
        self.car_development_controller = DummyCarDevelopmentController()

class DummyView:
    def __init__(self):
        self.SUBHEADER_FONT_SIZE = 16
        self.page_header_style = "header_style"
        self.clicked_button_style = "clicked_style"
        self.background_image = ft.Image(src="dummy.jpg")
        self.main_app = DummyMainApp()
        self.controller = DummyController()
        self.dark_grey = "#23232A"

# Dummy data class to simulate the car page data
class DummyCarPageData:
    def __init__(self, current_status, progress, car_speeds):
        self.current_status = current_status
        self.progress = progress
        self.car_speeds = car_speeds

# Dummy event classes to simulate flet control events
class DummyControl:
    def __init__(self, data):
        self.data = data

class DummyControlEvent:
    def __init__(self, control):
        self.control = control

# Import the modules under test (see :contentReference[oaicite:0]{index=0} and :contentReference[oaicite:1]{index=1})
from pw_view.car_page.car_page import CarPage, CarPageTabEnums
from pw_view.car_page.car_development_tab import CarDevelopmentTab
from pw_view.car_page.car_comparison_graph import CarComparisonGraph
from pw_model.car_development.car_development_model import CarDevelopmentStatusEnums


def test_car_development_tab_update():
    """Test that the CarDevelopmentTab updates correctly based on the status."""
    view = DummyView()
    tab = CarDevelopmentTab(view)

    # Test case: development in progress should disable development buttons
    data_in_progress = DummyCarPageData(CarDevelopmentStatusEnums.IN_PROGRESS.value, 50, [])
    tab.update_tab(data_in_progress)
    # Check that the status text is updated and buttons are disabled
    assert tab.current_status_text.value == f"Current Status: {CarDevelopmentStatusEnums.IN_PROGRESS.value.capitalize()}"
    assert tab.major_develop_btn.disabled is True
    assert tab.medium_develop_btn.disabled is True
    assert tab.minor_develop_btn.disabled is True

    # Test case: development not in progress should enable buttons
    data_ready = DummyCarPageData("ready", 0, [])
    tab.update_tab(data_ready)
    assert tab.current_status_text.value == "Current Status: Ready"
    assert tab.major_develop_btn.disabled is False
    assert tab.medium_develop_btn.disabled is False
    assert tab.minor_develop_btn.disabled is False

def test_start_development():
    """Test that clicking the start development button calls the controller with the correct data."""
    view = DummyView()
    tab = CarDevelopmentTab(view)
    # Simulate a control event with a dummy data value (e.g., "major")
    control = DummyControl("major")
    event = DummyControlEvent(control)
    tab.start_development(event)
    # Verify that the dummy controller received the 'major' selection
    assert view.controller.car_development_controller.selected == "major"

def test_car_page_display_tabs():
    """Test that the CarPage correctly displays tabs and updates button styles."""
    view = DummyView()
    page = CarPage(view)
    # Check that the page header "Car" is part of the controls
    header_texts = [ctrl.value for ctrl in page.controls if isinstance(ctrl, ft.Text)]
    assert "Car" in header_texts

    # Simulate clicking the car development button
    page.display_car_development(None)  # event not used in method logic
    assert page.car_development_btn.style == view.clicked_button_style

    # Ensure car_comparison_container is defined by calling update_page with dummy data
    dummy_data = DummyCarPageData("ready", 0, [("Team A", 80)])
    page.update_page(dummy_data)

    # Simulate clicking the car comparison button
    page.display_car_comparison(None)
    assert page.car_comparison_btn.style == view.clicked_button_style

def test_update_page():
    """Test that update_page correctly updates both the comparison graph and the development tab."""
    view = DummyView()
    page = CarPage(view)
    # Create dummy data with one team speed for the comparison graph
    data = DummyCarPageData("ready", 0, [("Team A", 80)])
    page.update_page(data)
    # Check that the comparison graph has one row corresponding to the team
    assert len(page.car_comparison_graph.controls) == 1
    # Verify the development tab status text update
    assert page.car_development_tab.current_status_text.value == "Current Status: Ready"
    # Confirm that the main_app update method was called
    assert view.main_app.updated is True
