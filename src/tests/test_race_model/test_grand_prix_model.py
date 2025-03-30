import pytest
import pandas as pd
from race_weekend_model.race_model_enums import ParticipantStatus, OvertakingStatus, SessionNames
from tests import create_model
from race_weekend_model.grand_prix_model import GrandPrixModel
from tests.test_model.track import test_track_model

class TestSetOvertakeStatus:
    @pytest.fixture
    def race_setup(self):
        model = create_model.create_model(mode="headless")
        track = test_track_model.create_dummy_track()
        race_model = create_model.create_race_model(model)
        
        # Create dummy qualifying results
        driver_names = [p.name for p in race_model.participants]
        race_model.results[SessionNames.QUALIFYING.value] = {
            "results": pd.DataFrame({
                "Driver": driver_names,
                "Position": range(1, len(driver_names) + 1)
            })
        }
        
        race_model.setup_race()
        return race_model.current_session

    def test_ahead_car_pitting(self, race_setup):
        participant = race_setup.race_weekend_model.participants[1]
        participant_ahead = race_setup.race_weekend_model.participants[0]
        participant_ahead.status = ParticipantStatus.PITTING_IN
        
        race_setup.set_overtake_status(participant, participant_ahead, delta=-1000, gap_ahead=300)
        assert participant.overtaking_status == OvertakingStatus.HOLD_BACK

    def test_ahead_car_retired(self, race_setup):
        participant = race_setup.race_weekend_model.participants[1]
        participant_ahead = race_setup.race_weekend_model.participants[0]
        participant_ahead.status = ParticipantStatus.RETIRED
        
        race_setup.set_overtake_status(participant, participant_ahead, delta=-1000, gap_ahead=300)
        assert participant.overtaking_status == OvertakingStatus.HOLD_BACK

    def test_ahead_car_attacking(self, race_setup):
        participant = race_setup.race_weekend_model.participants[1]
        participant_ahead = race_setup.race_weekend_model.participants[0]
        participant_ahead.overtaking_status = OvertakingStatus.ATTACKING
        
        race_setup.set_overtake_status(participant, participant_ahead, delta=-1000, gap_ahead=300)
        assert participant.overtaking_status == OvertakingStatus.HOLD_BACK

    def test_not_faster_than_ahead(self, race_setup):
        participant = race_setup.race_weekend_model.participants[1]
        participant_ahead = race_setup.race_weekend_model.participants[0]
        
        race_setup.set_overtake_status(participant, participant_ahead, delta=100, gap_ahead=300)
        assert participant.overtaking_status == OvertakingStatus.NONE

    def test_not_close_enough(self, race_setup):
        participant = race_setup.race_weekend_model.participants[1]
        participant_ahead = race_setup.race_weekend_model.participants[0]
        
        race_setup.set_overtake_status(participant, participant_ahead, delta=-100, gap_ahead=1000)
        assert participant.overtaking_status == OvertakingStatus.NONE

    def test_can_attack(self, race_setup):
        participant = race_setup.race_weekend_model.participants[1]
        participant_ahead = race_setup.race_weekend_model.participants[0]
        # Assuming track_model.overtaking_delta is less than 1000
        
        race_setup.set_overtake_status(participant, participant_ahead, delta=-1000, gap_ahead=300)
        assert participant.overtaking_status == OvertakingStatus.ATTACKING
