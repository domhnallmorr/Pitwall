import flet as ft
import pytest

from pw_view.car_page.car_page import CarPage
from pw_controller.car_development.car_page_data import CarPageData

# Dummy main_app with a simple update() spy mechanism
class DummyMainApp:
    def __init__(self):
        self.update_call_count = 0

    def update(self):
        self.update_call_count += 1

# Dummy view that supplies the needed attributes for CarPage
class DummyView:
    def __init__(self):
        self.SUBHEADER_FONT_SIZE = 16
        self.background_image = ft.Image(src="dummy.png")
        self.page_header_style = ft.TextThemeStyle.DISPLAY_MEDIUM
        self.main_app = DummyMainApp()
        self.dark_grey = "#23232A"

# The test for CarPage structure and update_page functionality
def test_car_page_structure_and_update(monkeypatch):
    view = DummyView()
    car_page_instance = CarPage(view)

    # --- Verify initial structure ---
    # CarPage is a ft.Column whose controls should contain a header text and a background stack.
    # The first control should be a Text widget with the text "Car"
    header = car_page_instance.controls[0]
    assert isinstance(header, ft.Text)
    assert header.value == "Car"

    # The second control should be a Stack containing the background image and the tabs.
    stack = car_page_instance.controls[1]
    assert isinstance(stack, ft.Stack)
    assert stack.controls[0] == view.background_image
    assert stack.controls[1] == car_page_instance.tabs

    # --- Setup spies to capture method calls ---
    setup_rows_called = False
    def fake_setup_rows(car_speeds):
        nonlocal setup_rows_called
        setup_rows_called = True
        fake_setup_rows.car_speeds = car_speeds

    update_tab_called = False
    def fake_update_tab(data):
        nonlocal update_tab_called
        update_tab_called = True
        fake_update_tab.data = data

    # Monkeypatch the methods in the CarComparisonGraph and CarDevelopmentTab instances
    monkeypatch.setattr(car_page_instance.car_comparison_graph, "setup_rows", fake_setup_rows)
    monkeypatch.setattr(car_page_instance.car_development_tab, "update_tab", fake_update_tab)

    # Record the current update call count of main_app
    initial_update_calls = view.main_app.update_call_count

    # --- Create a sample CarPageData instance ---
    data = CarPageData(
        car_speeds=[("Team A", 80), ("Team B", 90)],
        current_status="in_progress",
        progress=50
    )

    # Call update_page which should update both sub-components and then call view.main_app.update()
    car_page_instance.update_page(data)

    # Verify that the spy functions were called with the correct data.
    assert setup_rows_called, "Expected setup_rows to be called on CarComparisonGraph."
    assert fake_setup_rows.car_speeds == data.car_speeds, "Car speeds data not passed correctly to setup_rows."

    assert update_tab_called, "Expected update_tab to be called on CarDevelopmentTab."
    assert fake_update_tab.data == data, "Data not passed correctly to update_tab."

    # Verify that view.main_app.update was called (could be multiple times)
    assert view.main_app.update_call_count > initial_update_calls, "Expected main_app.update() to be called."

