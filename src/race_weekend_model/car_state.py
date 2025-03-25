from pw_model.track import track_model
from pw_model.tyre.tyre_compound import TyreCompound
from race_weekend_model.on_track_constants import TYRE_WEAR_INCREASE

class CarState:
    def __init__(self):
        self.fuel_load = 155  # kg
        self.tyre_wear = 0  # time lost (in ms) due to tyre wear

    def update_fuel(self, circuit_model: track_model.TrackModel) -> None:
        self.fuel_load -= circuit_model.fuel_consumption
        self.fuel_load = round(self.fuel_load, 2)

    def update_tyre_wear(self, circuit_model: track_model.TrackModel, tyre_compound: TyreCompound, new_tyres: bool=False) -> None:
        if new_tyres is False:
            # Get base wear from track
            base_wear = circuit_model.tyre_wear
            
            # Calculate additional wear based on tyre compound wear rating
            # A wear rating of 100 means no additional wear
            # A wear rating of 0 means maximum additional wear (TYRE_WEAR_INCREASE)
            tyre_compound_wear = int(TYRE_WEAR_INCREASE * (100 - tyre_compound.wear) / 100)
            
            # Add both wear components
            self.tyre_wear += base_wear + tyre_compound_wear
        else:  # made a pitstop, new tyres fitted
            self.tyre_wear = 0

    @property
    def fuel_effect(self) -> int:
        '''
        effect of fuel on lap time
        assume 1kg adds 0.03s to laptime
        '''
        return int(self.fuel_load * 30)

    def calculate_required_fuel(self, circuit_model: track_model.TrackModel, number_of_laps: int) -> int:
        number_of_laps_conservative = float(number_of_laps) + 0.5  # ensure half a lap of fuel is added for conservatism
        return int(number_of_laps_conservative * circuit_model.fuel_consumption)

    def setup_start_fuel_and_tyres(self, circuit_model: track_model.TrackModel, first_stop_lap: int) -> None:
        self.fuel_load = self.calculate_required_fuel(circuit_model, first_stop_lap)
        self.tyre_wear = 0  # fit new tyres
