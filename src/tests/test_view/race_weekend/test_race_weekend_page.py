import pytest
from unittest.mock import MagicMock
from pw_view.race_weekend.race_weekend_window import RaceWeekendWindow, SessionNames


@pytest.fixture
def mock_view():
    # Mocking the View dependency
    mock = MagicMock()
    mock.page_header_style = "default-style"
    mock.header2_style = "header2-style"
    mock.race_background_image = MagicMock()
    mock.main_app = MagicMock()
    mock.controller = MagicMock()
    return mock


@pytest.fixture
def race_data():
    return {
        "race_title": "Test Race Weekend"
    }


@pytest.fixture
def race_window(mock_view, race_data):
    return RaceWeekendWindow(view=mock_view, data=race_data)


def test_initialization(race_window):
    assert race_window.header_text.value == "Test Race Weekend"
    assert race_window.simulate_buttons[SessionNames.QUALIFYING].disabled is False
    assert race_window.simulate_buttons[SessionNames.RACE].disabled is True
    assert race_window.continue_btn.disabled is True


def test_simulate_qualifying(race_window):
    # Simulate clicking the Qualifying simulate button
    session_type = SessionNames.QUALIFYING
    mock_event = MagicMock()
    mock_event.control.data = session_type

    race_window.simulate(mock_event)

    # Check that the Qualifying button is disabled and the Race button is enabled
    assert race_window.simulate_buttons[session_type].disabled is True
    assert race_window.simulate_buttons[SessionNames.RACE].disabled is False
    assert session_type in race_window.simulate_btns_clicked


def test_simulate_race(race_window):
    # Simulate clicking the Race simulate button
    race_window.simulate_btns_clicked = [SessionNames.QUALIFYING]
    session_type = SessionNames.RACE
    mock_event = MagicMock()
    mock_event.control.data = session_type

    race_window.simulate(mock_event)

    # Check that the Race button is disabled and the Continue button is enabled
    assert race_window.simulate_buttons[session_type].disabled is True
    assert race_window.continue_btn.disabled is False
    assert session_type in race_window.simulate_btns_clicked


def test_return_to_main_window(race_window):
    mock_event = MagicMock()

    # Trigger the return to main window method
    race_window.return_to_main_window(mock_event)

    # Check that the Continue button is disabled again
    assert race_window.continue_btn.disabled is True
    race_window.view.main_app.update.assert_called_once()
    race_window.view.controller.post_race_actions.assert_called_once()
