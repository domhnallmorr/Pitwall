from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING
from pw_model.car_development.car_development_model import CarDevelopmentEnums, CarDevelopmentStatusEnums

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model

@dataclass(frozen=True)
class CarPageData:
	"""Data structure for car page information"""
	car_speed_history: dict[str, list[int]]
	team_colors: dict[str, str]
	countries: list[str]
	current_status: str
	progress: float = 0.0  # Add progress field, defaulting to 0
	testing_progress: int = 0  # Add testing progress field, defaulting to 0
	# Add engine supplier data
	engine_supplier_name: str = ""
	engine_supplier_deal: str = ""
	engine_power: int = 0
	engine_resources: int = 0
	engine_overall_rating: int = 0

	# Add tyre supplier data
	tyre_supplier_name: str = ""
	tyre_supplier_deal: str = ""
	tyre_grip: int = 0
	tyre_wear: int = 0

	# car speed history



def get_car_page_data(model: Model) -> CarPageData:
	"""Creates CarPageData from the model"""
	# car_speeds = [(team.name, team.car_model.speed) for team in model.teams]
	# car_speeds.sort(key=lambda x: x[1], reverse=True)  # sort, highest speed to lowest speed
	
	car_dev_model = model.player_team_model.car_development_model
	testing_model = model.player_team_model.testing_model
	engine_supplier_model = model.player_team_model.engine_supplier_model
	engine_supplier_deal = model.player_team_model.supplier_model.engine_supplier_deal
	tyre_supplier_model = model.player_team_model.tyre_supplier_model
	tyre_supplier_deal = model.player_team_model.supplier_model.tyre_supplier_deal

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

	# get car speed history
	car_speed_history = {}
	team_colors = {}
	for team in model.teams:
		car_speed_history[team.name] = team.car_development_model.car_speed_history
		team_colors[team.name] = team.team_colors_manager.primary_colour

	return CarPageData(
		car_speed_history=car_speed_history,
		team_colors=team_colors,
		countries=model.season.calendar.countries,
		current_status=car_dev_model.current_status.value,  # Changed from status to current_status
		progress=progress,
		testing_progress=testing_model.testing_progress,  # Changed from testing_progress to testing_progress
		engine_supplier_name=engine_supplier_model.name,
		engine_supplier_deal=engine_supplier_deal.value,
		engine_power=engine_supplier_model.power,
		engine_resources=engine_supplier_model.resources,
		engine_overall_rating=engine_supplier_model.overall_rating,

		tyre_supplier_name=tyre_supplier_model.name,
		tyre_supplier_deal=tyre_supplier_deal.value, # Changed from deal to tyre_supplier_deal
		tyre_grip=tyre_supplier_model.compound.grip,
		tyre_wear=tyre_supplier_model.compound.wear,
	)
