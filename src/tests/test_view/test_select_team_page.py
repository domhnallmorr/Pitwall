# import unittest
from unittest.mock import Mock

from pw_view.title_screen.team_selection_screen import TeamSelectionScreen

def test_team_button_click_calls_controller():
    mock_controller = Mock()

    mock_view = Mock()
    mock_view.controller = mock_controller
    
    team_names = ["Williams", "Ferrari", "McLaren"]

    screen = TeamSelectionScreen(mock_view, team_names)

    ferrari_button = screen.controls[1].controls[1]

    mock_event = Mock()
    mock_event.control = Mock()
    mock_event.control.data = "Ferrari"

    ferrari_button.on_click(mock_event)

    mock_controller.start_career.assert_called_once_with("Ferrari")

def test_team_buttons_setup_correctly():
    # Mock the view
    mock_view = Mock()

    # Sample team names
    team_names = ["Williams", "Ferrari", "McLaren", "Benetton"]

    # Create the TeamSelectionScreen
    screen = TeamSelectionScreen(mock_view, team_names)

    # Access the buttons (inside the ft.Column)
    buttons_column = screen.controls[1]  # The second control is the ft.Column
    team_buttons = buttons_column.controls

    # Verify the number of buttons matches the number of teams
    assert len(team_buttons) == len(team_names)

    # Verify each button's label matches the team name
    for button, team_name in zip(team_buttons, team_names):
        assert button.text == team_name