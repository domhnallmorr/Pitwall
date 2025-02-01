import pytest
from unittest.mock import Mock
import os
import numpy as np

import matplotlib.pyplot as plt

from race_weekend_model.laptime_manager import LapTimeManager, LapManagerRandomiser
from race_weekend_model.race_model_enums import ParticipantStatus
from tests.test_model.track import test_track_model

@pytest.fixture
def mock_participant():
    """Mocked ParticipantModel with essential attributes."""
    mock = Mock()
    mock.track_model = test_track_model.create_dummy_track()
    mock.driver.speed = 90
    mock.driver.consistency = 50
    mock.car_model.speed = 85
    mock.car_model.fuel_effect = 0.3
    mock.car_model.tyre_wear = 0.2
    mock.track_model.base_laptime = 90000  # Base lap time in ms
    mock.track_model.pit_stop_loss = 20000
    mock.pitstop_times = [8000]
    mock.participant.status = ParticipantStatus.RUNNING

    return mock

@pytest.fixture
def mock_randomiser():
    """Mocked LapManagerRandomiser."""
    mock = Mock(spec=LapManagerRandomiser)
    mock.random_lap1_time_loss.return_value = 500  # 500ms random variation for lap 1
    mock.random_laptime_loss.return_value = 100  # 100ms random variation for general laps
    return mock

@pytest.fixture
def lap_time_manager(mock_participant, mock_randomiser):
    """LapTimeManager with mocked participant and randomiser."""
    laptime_manager = LapTimeManager(mock_participant)
    laptime_manager.randomiser = mock_randomiser
    laptime_manager.setup_variables_for_session()

    return laptime_manager

def test_calculate_base_laptime(lap_time_manager, mock_participant):
    """Test calculation of base lap time."""
    lap_time_manager.calculate_base_laptime()
    expected_base = (
        mock_participant.track_model.base_laptime
        + (100 - mock_participant.driver.speed) * 20  # DRIVER_SPEED_FACTOR
        + (100 - mock_participant.car_model.speed) * 50  # CAR_SPEED_FACTOR
    )
    assert lap_time_manager.base_laptime == expected_base

def test_calculate_laptime(lap_time_manager, mock_participant, mock_randomiser):
    """Test lap time calculation with randomiser and dirty air."""
    dirty_air_effect = 200  # ms
    lap_time_manager.calculate_laptime(dirty_air_effect)

    expected_laptime = (
        lap_time_manager.base_laptime
        + mock_randomiser.random_laptime_loss()
        + mock_participant.car_model.fuel_effect
        + mock_participant.car_model.tyre_wear
        + dirty_air_effect
    )

    assert lap_time_manager.laptime == expected_laptime

def test_complete_lap(lap_time_manager):
    """Test recording of a completed lap."""
    lap_time_manager.laptime = 92000  # ms
    lap_time_manager.complete_lap()
    assert lap_time_manager.laptimes == [92000]

def test_calculate_first_lap_laptime(lap_time_manager, mock_randomiser, mock_participant):
    """Test first lap time calculation."""
    idx = 5  # Position after turn 1
    lap_time_manager.calculate_first_lap_laptime(idx)

    expected_laptime = (
        mock_participant.track_model.base_laptime
        + 6000  # LAP1_TIME_LOSS
        + idx * 1000  # LAP1_TIME_LOSS_PER_POSITION
        + mock_randomiser.random_lap1_time_loss()
    )

    assert lap_time_manager.laptime == expected_laptime

def test_recalculate_laptime_when_passed(lap_time_manager):
    """Test recalculation of lap time when passed."""
    lap_time_manager.laptime = 92000
    lap_time_manager.laptimes = [92000]

    revised_laptime = 93000  # ms
    lap_time_manager.recalculate_laptime_when_passed(revised_laptime)

    assert lap_time_manager.laptime == revised_laptime
    assert lap_time_manager.laptimes[-1] == revised_laptime

def test_total_time_property(lap_time_manager):
    """Test total time property."""
    lap_time_manager.laptimes = [92000, 91000, 93000]
    assert lap_time_manager.total_time == sum(lap_time_manager.laptimes)

def test_fastest_lap_property(lap_time_manager):
    """Test fastest lap property."""
    lap_time_manager.laptimes = [92000, 91000, 93000]
    assert lap_time_manager.fastest_lap == 91000

def test_fastest_lap_property_empty(lap_time_manager):
    """Test fastest lap property when no laps are recorded."""
    lap_time_manager.laptimes = []
    assert lap_time_manager.fastest_lap is None

def test_calculate_laptime_pitting_in(lap_time_manager, mock_participant, mock_randomiser):
    """Test lap time calculation when participant is pitting in."""
    mock_participant.status = ParticipantStatus.PITTING_IN
    dirty_air_effect = 0  # No dirty air effect during pitting

    lap_time_manager.calculate_laptime(dirty_air_effect)

    expected_laptime = (
        lap_time_manager.base_laptime
        + mock_randomiser.random_laptime_loss()
        + mock_participant.car_model.fuel_effect
        + mock_participant.car_model.tyre_wear
        + mock_participant.track_model.pit_stop_loss
        + mock_participant.pitstop_times[-1]
    )

    assert lap_time_manager.laptime == expected_laptime

@pytest.fixture
def simulate_laps():
    """Simulate laps for a driver with a given consistency using the real randomiser."""
    def _simulate(consistency, num_laps=20):
        mock_participant = Mock()
        mock_participant.track_model.base_laptime = 90000  # Base lap time in ms
        mock_participant.driver.speed = 90
        mock_participant.driver.consistency = consistency
        mock_participant.car_model.speed = 85
        mock_participant.car_model.fuel_effect = 0.3
        mock_participant.car_model.tyre_wear = 0.2
        mock_participant.track_model.pit_stop_loss = 20000
        mock_participant.pitstop_times = [8000]
        mock_participant.status = ParticipantStatus.RUNNING

        # ** Use the real LapTimeManager **
        lap_time_manager = LapTimeManager(mock_participant)
        lap_time_manager.setup_variables_for_session()  # Ensure lap times list is initialized

        # ** FIX: Assign LapTimeManager to the participant **
        mock_participant.laptime_manager = lap_time_manager  # Critical Fix

        lap_times = []
        for _ in range(num_laps):
            lap_time_manager.calculate_laptime(dirty_air_effect=0)  # Calculate lap time using real randomiser
            lap_time_manager.complete_lap()
            lap_times.append(lap_time_manager.laptime)

        return lap_times

    return _simulate

def test_plot_consistency_effect(simulate_laps):
    """Test that saves the effect of consistency on lap times as a JPEG file."""
    num_laps = 60
    driver_A_consistency = 90  # More consistent driver
    driver_B_consistency = 20  # Less consistent driver

    laps_A = simulate_laps(driver_A_consistency, num_laps)
    laps_B = simulate_laps(driver_B_consistency, num_laps)

    # Plot results
    plt.figure(figsize=(10, 6))
    plt.plot(range(1, num_laps + 1), laps_A, label=f"Driver A (Consistency: {driver_A_consistency})", marker='o')
    plt.plot(range(1, num_laps + 1), laps_B, label=f"Driver B (Consistency: {driver_B_consistency})", marker='s', linestyle='dashed')

    plt.xlabel("Lap Number")
    plt.ylabel("Lap Time (ms)")
    plt.title("Effect of Consistency on Lap Times")
    plt.legend()
    plt.grid(True)

    # Ensure the directory exists
    output_dir = os.path.dirname(__file__)  # Get test script directory
    output_path = os.path.join(output_dir, "lap_time_consistency.jpg")

    plt.savefig(output_path, format='jpeg', dpi=300)  # Save the figure as a JPEG
    plt.close()  # Close the plot to free memory

    # Check if file exists to confirm it was saved
    assert os.path.exists(output_path), f"Graph not saved at {output_path}"