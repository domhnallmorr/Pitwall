import pytest
import flet as ft
from unittest.mock import MagicMock

# Import the TeamSelectionScreen from its module.
# Adjust the import below to match your project structure.
from pw_view.team_selection.team_selection_screen import TeamSelectionScreen


# Create dummy controller and view objects to simulate the dependencies.
class DummyController:
    def __init__(self):
        # The team_selection_controller will be a MagicMock to verify that its team_selected() method is called.
        self.team_selection_controller = MagicMock()
        # start_career is also a MagicMock so we can assert it is called.
        self.start_career = MagicMock()


class DummyView:
    def __init__(self):
        # Provide the required attributes used in your TeamSelectionScreen
        self.dark_grey = "dark_grey"
        self.page_header_style = "header_style"
        self.background_image = "dummy_background"
        self.SUBHEADER_FONT_SIZE = 20
        self.controller = DummyController()
        self.positive_button_style = ft.ButtonStyle(color="#111418",
											  icon_color="#111418",
											  bgcolor={ft.ControlState.DEFAULT: ft.Colors.LIGHT_GREEN, ft.ControlState.DISABLED: ft.Colors.GREY},
											  alignment=ft.alignment.center_left,)

        self.team_logos_path = "path/to/team/logos"
        self.flags_small_path = "path/to/flags"


# Helper classes to simulate an event (flet.ControlEvent)
class DummyControl:
    pass


class DummyEvent:
    def __init__(self, data):
        # Simulate an event where e.control.data contains the team name.
        self.control = DummyControl()
        self.control.data = data


# Test that upon initialization the first team is selected.
def test_team_selection_initial_state():
    dummy_view = DummyView()
    team_names = ["Team A", "Team B", "Team C"]
    team_countries = ["Country A", "Country B", "Country C"]
    screen = TeamSelectionScreen(dummy_view, team_names, team_countries)

    # The default selected team should be the first one.
    assert screen.selected_team == "Team A"

    # The first button should have the PRIMARY color, while the others have GREY.
    assert screen.team_buttons[0].bgcolor == ft.Colors.PRIMARY
    for btn in screen.team_buttons[1:]:
        assert btn.bgcolor == ft.Colors.GREY


# Test that update_team_details properly updates the selected team and button colors.
def test_update_team_details():
    dummy_view = DummyView()
    team_names = ["Team A", "Team B", "Team C"]
    team_countries = ["Country A", "Country B", "Country C"]
    screen = TeamSelectionScreen(dummy_view, team_names, team_countries)

    # Simulate the user clicking on "Team B".
    event = DummyEvent("Team B")
    screen.update_team_details(event)

    # The selected team should now be "Team B".
    assert screen.selected_team == "Team B"

    # Check that the previously selected button ("Team A") is now GREY and "Team B" is PRIMARY.
    assert screen.team_buttons[0].bgcolor == ft.Colors.GREY   # "Team A" unselected.
    assert screen.team_buttons[1].bgcolor == ft.Colors.PRIMARY  # "Team B" selected.
    assert screen.team_buttons[2].bgcolor == ft.Colors.GREY       # "Team C" remains unselected.

    # Verify that the team_selected method was called with "Team B".
    dummy_view.controller.team_selection_controller.team_selected.assert_called_once_with("Team B")


# Test that start_career calls the corresponding controller method with the current selected team.
def test_start_career():
    dummy_view = DummyView()
    team_names = ["Team A", "Team B", "Team C"]
    team_countries = ["Country A", "Country B", "Country C"]    
    screen = TeamSelectionScreen(dummy_view, team_names, team_countries)

    # For extra fun, simulate updating the selection to "Team C" before starting the career.
    update_event = DummyEvent("Team C")
    screen.update_team_details(update_event)

    # Now simulate clicking the Start Career button.
    dummy_event = DummyEvent("irrelevant")  # the data isn't used in start_career
    screen.start_career(dummy_event)

    # Verify that the controller's start_career method was called with "Team C".
    dummy_view.controller.start_career.assert_called_once_with("Team C")
