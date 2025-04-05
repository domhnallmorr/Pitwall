from unittest.mock import patch
from tests import create_model
from race_weekend_model import race_weekend_model
from race_weekend_model.race_model_enums import SessionNames, SessionMode
from race_weekend_model.race_start_calculations import calculate_run_to_turn1
from tests.test_model.track import test_track_model

def test_turn1_incident_impact():
    # Setup race model
    model = create_model.create_model(mode="headless")
    track = test_track_model.create_dummy_track()
    _race_model = race_weekend_model.RaceWeekendModel("headless", model, track)

    # Run qualy to establish a grid order
    _race_model.setup_qualifying(60*60, SessionNames.QUALIFYING)
    _race_model.setup_race()
    _race_model.current_session.mode = SessionMode.SIMULATE

    # Force a turn 1 incident for the leader
    with patch.object(_race_model.randomiser, 'turn1_incident_occurred', return_value=0), \
         patch.object(_race_model.randomiser, 'spin_victim_idx', return_value=0), \
         patch.object(_race_model.randomiser, 'turn1_spin_time_loss', return_value=25_000):
        
        order_after_turn1 = calculate_run_to_turn1(_race_model)
        
        # Find the driver with the highest time to turn 1 (the spun driver)
        leader_time = min(order_after_turn1, key=lambda x: x[0])[0]
        spun_driver_entry = max(order_after_turn1, key=lambda x: x[0])
        spun_driver = spun_driver_entry[1]
        spun_driver_time = spun_driver_entry[0]
        
        time_behind_leader = (spun_driver_time - leader_time) / 1000  # Convert to seconds
        
        print(f"\nSpun driver identified as: {spun_driver.name}")
        print(f"Initial time behind leader: {time_behind_leader:.1f} seconds")
        
        # Assert the initial time gap is at least 20 seconds (since we forced a 25s penalty)
        assert time_behind_leader >= 20, f"Expected initial time gap of at least 20s, but got {time_behind_leader:.1f}s"
        
        # Print initial order after Turn 1
        print("\nOrder after Turn 1:")
        for time, driver in order_after_turn1:
            gap_to_leader = (time - leader_time) / 1000
            print(f"{driver.name}: {time}ms (+{gap_to_leader:.1f}s)")
        
        # Simulate 2 more laps
        for lap in range(2):
            _race_model.current_session.advance(mode=SessionMode.SIMULATE)
            print(f"\nOrder after lap {lap + 1}:")
            current_order = _race_model.current_session.standings_model.current_order
            for pos, driver in enumerate(current_order, 1):
                print(f"{pos}. {driver}")
        
        # Get the spun driver's final position and gap
        standings_df = _race_model.current_session.standings_model.dataframe
        leader_row = standings_df.iloc[0]
        spun_driver_row = standings_df[standings_df["Driver"] == spun_driver.name].iloc[0]
        final_gap = (spun_driver_row["Gap to Leader"] / 1000) if "Gap to Leader" in standings_df.columns else None
        
        print(f"\nFinal position of spun driver {spun_driver.name}: {spun_driver_row.name + 1}")
        if final_gap is not None:
            print(f"Final time behind leader: {final_gap:.1f} seconds")
            # Assert the final time gap is still at least 15 seconds
            assert final_gap >= 15, f"Expected final time gap of at least 15s, but got {final_gap:.1f}s"
        
        # Assert the spun driver is last
        assert spun_driver_row.name == len(standings_df) - 1
