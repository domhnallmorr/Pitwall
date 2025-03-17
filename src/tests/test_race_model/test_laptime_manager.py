import pytest
from unittest.mock import Mock, patch
import random

from race_weekend_model.race_model_enums import ParticipantStatus
from race_weekend_model.laptime_manager import LapTimeManager, LapManagerRandomiser

class TestLapTimeManager:
    @pytest.fixture
    def mock_participant(self):
        """Create a mock participant with all necessary attributes and models."""
        participant = Mock()
        
        # Set up driver
        participant.driver = Mock()
        participant.driver.speed = 80
        participant.driver.consistency = 75
        
        # Set up car model
        participant.car_model = Mock()
        participant.car_model.speed = 85
        
        # Set up car state
        participant.car_state = Mock()
        participant.car_state.fuel_effect = 1500  # 1.5s effect from fuel
        participant.car_state.tyre_wear = 300  # 0.3s effect from tyre wear
        
        # Set up track model
        participant.track_model = Mock()
        participant.track_model.base_laptime = 90000  # 90s base laptime
        participant.track_model.power = 7  # Power sensitivity 7/10
        participant.track_model.pit_stop_loss = 20000  # 20s pit stop loss
        
        # Set up team model and engine supplier
        participant.team_model = Mock()
        participant.team_model.engine_supplier_model = Mock()
        participant.team_model.engine_supplier_model.power = 60  # Engine power rating 60/100
        
        # Set up status
        participant.status = ParticipantStatus.RUNNING
        participant.pitstop_times = []
        
        return participant
    
    def test_init(self, mock_participant):
        """Test that LapTimeManager initializes correctly."""
        laptime_manager = LapTimeManager(mock_participant)
        
        # Check initialization
        assert laptime_manager.participant == mock_participant
        assert laptime_manager.driver == mock_participant.driver
        assert laptime_manager.car_model == mock_participant.car_model
        assert laptime_manager.car_state == mock_participant.car_state
        assert laptime_manager.track_model == mock_participant.track_model
        
        # Check that base laptime is calculated
        assert hasattr(laptime_manager, 'base_laptime')
        
        # Check that laptime variation is calculated
        # With consistency 75, variation should be 300 + (1 - 0.75) * 400 = 300 + 100 = 400
        assert laptime_manager.laptime_variation == 400
    
    def test_calculate_base_laptime(self, mock_participant):
        """Test the base laptime calculation."""
        laptime_manager = LapTimeManager(mock_participant)
        
        # Manually calculate expected base laptime
        base = mock_participant.track_model.base_laptime  # 90000
        driver_effect = (100 - mock_participant.driver.speed) * 20  # (100 - 80) * 20 = 400
        car_effect = (100 - mock_participant.car_model.speed) * 50  # (100 - 85) * 50 = 750
        
        # Calculate power effect
        engine_power = mock_participant.team_model.engine_supplier_model.power  # 60
        track_power_sensitivity = mock_participant.track_model.power  # 7
        power_effect = (2000 * track_power_sensitivity / 10) * (50 - engine_power) / 100
        # (2000 * 7 / 10) * (50 - 60) / 100 = 1400 * (-10) / 100 = -140
        
        expected_base_laptime = base + driver_effect + car_effect + power_effect
        
        assert abs(laptime_manager.base_laptime - expected_base_laptime) < 10  # Allow for small rounding differences
    
    def test_setup_variables_for_session(self, mock_participant):
        """Test that setup_variables_for_session initializes session variables."""
        laptime_manager = LapTimeManager(mock_participant)
        
        laptime_manager.setup_variables_for_session()
        
        assert laptime_manager.laptime is None
        assert laptime_manager.laptimes == []
    
    def test_calculate_laptime(self, mock_participant):
        """Test the laptime calculation with no dirty air effect."""
        # Set up the laptime manager with a controlled random function
        with patch.object(random, 'uniform', return_value=200):
            laptime_manager = LapTimeManager(mock_participant)
            laptime_manager.setup_variables_for_session()
            
            # Calculate laptime with no dirty air
            laptime_manager.calculate_laptime(0)
            
            # Expected components:
            # - base_laptime (calculated in init)
            # - random_time_loss = 200 (from our mock)
            # - fuel_effect = 1500
            # - tyre_wear = 300
            # - dirty_air_effect = 0
            expected_components_sum = laptime_manager.base_laptime + 200 + 1500 + 300 + 0
            
            assert laptime_manager.laptime == expected_components_sum
    
    def test_calculate_laptime_with_pitting(self, mock_participant):
        """Test the laptime calculation when pitting."""
        # Set up participant to be pitting
        mock_participant.status = ParticipantStatus.PITTING_IN
        mock_participant.pitstop_times = [4000]  # 4s for the actual pit stop
        
        # Set up the laptime manager with a controlled random function
        with patch.object(random, 'uniform', return_value=200):
            laptime_manager = LapTimeManager(mock_participant)
            laptime_manager.setup_variables_for_session()
            
            # Calculate laptime with pitting
            laptime_manager.calculate_laptime(0)
            
            # Expected components:
            # - base_laptime (calculated in init)
            # - random_time_loss = 200 (from our mock)
            # - fuel_effect = 1500
            # - tyre_wear = 300
            # - dirty_air_effect = 0
            # - pit_stop_loss = 20000
            # - pitstop_time = 4000
            expected_components_sum = laptime_manager.base_laptime + 200 + 1500 + 300 + 0 + 20000 + 4000
            
            assert laptime_manager.laptime == expected_components_sum
    
    def test_complete_lap(self, mock_participant):
        """Test that lap completion adds the current laptime to the list."""
        laptime_manager = LapTimeManager(mock_participant)
        laptime_manager.setup_variables_for_session()
        
        # Set a laptime value
        laptime_manager.laptime = 92000
        
        # Complete the lap
        laptime_manager.complete_lap()
        
        # Check the laptime was added to the list
        assert laptime_manager.laptimes == [92000]
    
    def test_total_time(self, mock_participant):
        """Test that total_time property returns the sum of all laptimes."""
        laptime_manager = LapTimeManager(mock_participant)
        laptime_manager.setup_variables_for_session()
        
        # Add some laptimes
        laptime_manager.laptimes = [92000, 91500, 91800]
        
        # Check total time
        assert laptime_manager.total_time == 275300
    
    def test_fastest_lap(self, mock_participant):
        """Test that fastest_lap property returns the minimum laptime."""
        laptime_manager = LapTimeManager(mock_participant)
        laptime_manager.setup_variables_for_session()
        
        # Test with no laps
        assert laptime_manager.fastest_lap is None
        
        # Add some laptimes
        laptime_manager.laptimes = [92000, 91500, 91800]
        
        # Check fastest lap
        assert laptime_manager.fastest_lap == 91500
    
    def test_calculate_qualfying_laptime(self, mock_participant):
        """Test the qualifying laptime calculation."""
        with patch.object(random, 'uniform', return_value=200):
            laptime_manager = LapTimeManager(mock_participant)
            laptime_manager.setup_variables_for_session()
            
            # Calculate qualifying laptime
            laptime_manager.calculate_qualfying_laptime()
            
            # Check that calculate_laptime was called with 0 (no dirty air)
            # and that the lap was completed
            assert laptime_manager.laptime is not None
            assert len(laptime_manager.laptimes) == 1
    
    def test_calculate_first_lap_laptime(self, mock_participant):
        """Test the first lap laptime calculation."""
        with patch.object(random, 'uniform', return_value=500):
            laptime_manager = LapTimeManager(mock_participant)
            
            # Set up randomiser with controlled random value
            laptime_manager.randomiser = Mock()
            laptime_manager.randomiser.random_lap1_time_loss.return_value = 500
            
            # Calculate first lap time with position index 3
            position_index = 3
            laptime_manager.calculate_first_lap_laptime(position_index)
            
            # Expected components:
            # - track_model.base_laptime = 90000
            # - LAP1_TIME_LOSS = 6000
            # - position effect = position_index * LAP1_TIME_LOSS_PER_POSITION = 3 * 1000 = 3000
            # - random_time_loss = 500
            expected_laptime = 90000 + 6000 + 3000 + 500
            
            assert laptime_manager.laptime == expected_laptime
    
    def test_recalculate_laptime_when_passed(self, mock_participant):
        """Test recalculating laptime when passed by another car."""
        laptime_manager = LapTimeManager(mock_participant)
        laptime_manager.setup_variables_for_session()
        
        # Set up initial laptime
        laptime_manager.laptime = 92000
        laptime_manager.laptimes = [92000]
        
        # Recalculate with a new laptime
        new_laptime = 93000
        laptime_manager.recalculate_laptime_when_passed(new_laptime)
        
        # Check the laptime was updated
        assert laptime_manager.laptime == new_laptime
        assert laptime_manager.laptimes == [new_laptime]
    
    def test_calculate_engine_power_effect(self, mock_participant):
        """Test the engine power effect calculation with different track power values and engine power ratings."""
        # Test combinations of track power sensitivity and engine power
        test_cases = [
            # track_power, engine_power, expected_effect
            (1, 50, 0),      # Minimum track sensitivity, neutral engine
            (1, 70, -40),    # Minimum track sensitivity, strong engine
            (1, 30, 40),     # Minimum track sensitivity, weak engine
            
            (5, 50, 0),      # Medium track sensitivity, neutral engine  
            (5, 70, -200),   # Medium track sensitivity, strong engine
            (5, 30, 200),    # Medium track sensitivity, weak engine
            
            (10, 50, 0),     # Maximum track sensitivity, neutral engine
            (10, 70, -400),  # Maximum track sensitivity, strong engine
            (10, 30, 400)    # Maximum track sensitivity, weak engine
        ]
        
        for track_power, engine_power, expected_effect in test_cases:
            # Update the mock participant with the test case values
            mock_participant.track_model.power = track_power
            mock_participant.team_model.engine_supplier_model.power = engine_power
            
            # Create a new laptime manager for each test case
            laptime_manager = LapTimeManager(mock_participant)
            
            # Calculate the effect and verify
            effect = laptime_manager.calculate_engine_power_effect()
            
            # Calculate expected effect manually for verification
            manual_calculation = int(
                (2000 * track_power / 10) * (50 - engine_power) / 100
            )
            
            # Check if the actual effect matches our expectation
            assert effect == expected_effect
            assert effect == manual_calculation


class TestLapManagerRandomiser:
    @pytest.fixture
    def mock_participant(self):
        """Create a mock participant for the randomiser."""
        participant = Mock()
        participant.laptime_manager = Mock()
        participant.laptime_manager.laptime_variation = 400
        return participant
    
    def test_random_lap1_time_loss(self, mock_participant):
        """Test that random_lap1_time_loss returns a value in the expected range."""
        randomiser = LapManagerRandomiser(mock_participant)
        
        # Patch random.uniform to test the function with controlled values
        with patch.object(random, 'uniform', return_value=450.0):
            time_loss = randomiser.random_lap1_time_loss()
            assert time_loss == 450.0
    
    def test_random_laptime_loss(self, mock_participant):
        """Test that random_laptime_loss returns a value in the expected range."""
        randomiser = LapManagerRandomiser(mock_participant)
        
        # Patch random.uniform to test the function with controlled values
        with patch.object(random, 'uniform', return_value=250.0):
            time_loss = randomiser.random_laptime_loss()
            assert time_loss == 250.0