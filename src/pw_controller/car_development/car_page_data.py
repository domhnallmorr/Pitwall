from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING
from pw_model.car_development.car_development_model import CarDevelopmentEnums, CarDevelopmentStatusEnums

if TYPE_CHECKING:
    from pw_model.pw_base_model import Model

@dataclass(frozen=True)
class CarPageData:
    """Data structure for car page information"""
    car_speeds: list[tuple[str, int]]  # List of (team_name, car_speed) tuples
    current_status: str
    progress: float = 0.0  # Add progress field, defaulting to 0

def get_car_page_data(model: Model) -> CarPageData:
    """Creates CarPageData from the model"""
    car_speeds = [(team.name, team.car_model.speed) for team in model.teams]
    car_speeds.sort(key=lambda x: x[1], reverse=True)  # sort, highest speed to lowest speed
    
    car_dev_model = model.player_team_model.car_development_model
    # Calculate progress as percentage (time completed / total time)
    progress = 0.0
    if car_dev_model.current_status == CarDevelopmentStatusEnums.IN_PROGRESS:
        if car_dev_model.current_development_type == CarDevelopmentEnums.MAJOR:
            total_time = 10
        elif car_dev_model.current_development_type == CarDevelopmentEnums.MEDIUM:
            total_time = 7
        else:  # MINOR
            total_time = 5
        time_completed = total_time - car_dev_model.time_left
        progress = (time_completed / total_time) * 100
    
    return CarPageData(
        car_speeds=car_speeds,
        current_status=car_dev_model.current_status.value,
        progress=progress
    )
