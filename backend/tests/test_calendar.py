import pytest
from unittest.mock import MagicMock, patch
from app.models.calendar import Calendar, Event, EventType
from app.models.circuit import Circuit
from app.main import process_command, CURRENT_STATE

# Fixtures for data
@pytest.fixture
def sample_circuits():
    return [
        Circuit(id=1, name="Melb", country="Australia", location="Melb", laps=58, base_laptime_ms=90000, length_km=5.3, overtaking_delta=0.5, power_factor=0.5, track_map_path=""),
        Circuit(id=2, name="Monaco", country="Monaco", location="Monaco", laps=78, base_laptime_ms=75000, length_km=3.3, overtaking_delta=0.9, power_factor=0.2, track_map_path="")
    ]

@pytest.fixture
def sample_events():
    return [
        Event(name="Melb", week=5, type=EventType.RACE),
        Event(name="Test1", week=2, type=EventType.TEST),
        Event(name="Monaco", week=10, type=EventType.RACE)
    ]

def test_get_schedule_data_formatting(sample_events, sample_circuits):
    """
    Test that get_schedule_data returns correct format and enriched data.
    """
    # Create calendar with out-of-order events to test sorting (though sorting happens in DB usually, 
    # the method itself iterates the list as given. We assume the list passed to logic is sorted)
    # Actually, let's just test the formatting logic here.
    
    calendar = Calendar(events=sample_events, current_week=1)
    
    schedule = calendar.get_schedule_data(sample_circuits)
    
    assert len(schedule) == 3
    
    # Check Test Event
    test_evt = next(s for s in schedule if s['week'] == 2)
    assert test_evt['round'] == '-'
    assert test_evt['type'] == 'Test'
    assert test_evt['country'] == 'Unknown' # "Test1" not in circuits
    
    # Check Race Event 1
    race1 = next(s for s in schedule if s['week'] == 5)
    assert race1['round'] == '1'
    assert race1['type'] == 'Grand Prix'
    assert race1['country'] == 'Australia' # Lookup worked
    
    # Check Race Event 2
    race2 = next(s for s in schedule if s['week'] == 10)
    assert race2['round'] == '2'
    assert race2['country'] == 'Monaco'

@patch('app.main.CURRENT_STATE')
def test_get_calendar_api(mock_state, sample_events, sample_circuits):
    """
    Test the 'get_calendar' command via process_command.
    """
    # Setup Mock State
    mock_state.calendar = Calendar(events=sample_events)
    mock_state.circuits = sample_circuits
    
    cmd = {'type': 'get_calendar'}
    response = process_command(cmd)
    
    assert response['status'] == 'success'
    assert response['type'] == 'calendar_data'
    assert len(response['data']) == 3
    assert response['data'][0]['track'] == 'Melb' # Order preserved from events list passed 
