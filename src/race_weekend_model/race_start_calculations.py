from __future__ import annotations
import random
from typing import TYPE_CHECKING, TypeAlias

import pandas as pd

from race_weekend_model.on_track_constants import TURN1_INCIDENT_CHANCE
from race_weekend_model.particpant_model import ParticpantModel
from race_weekend_model.race_model_enums import SessionMode

if TYPE_CHECKING:
	from race_weekend_model.race_weekend_model import RaceWeekendModel

order_after_turn1_list: TypeAlias = list[tuple[float, ParticpantModel]]

def calculate_run_to_turn1(race_weekend_model: RaceWeekendModel) -> order_after_turn1_list:

	dist_to_turn1 = race_weekend_model.track_model.dist_to_turn1
	AVERAGE_SPEED = 47.0 #m/s

	order_after_turn1: order_after_turn1_list = []
	standings_df = race_weekend_model.current_session.standings_model.dataframe.copy(deep=True)

	for idx, p in enumerate([race_weekend_model.get_particpant_model_by_name(n) for n in standings_df["Driver"].values.tolist()]):
		random_factor = race_weekend_model.randomiser.run_to_turn1_random_factor(p.name)
		time_to_turn1: float = round(dist_to_turn1 / (AVERAGE_SPEED + random_factor), 3)
		time_to_turn1 = int(time_to_turn1 * 1000) # convert to ms
		particpant_model: ParticpantModel = p
		order_after_turn1.append([time_to_turn1, particpant_model])
		
		dist_to_turn1 += 5 # add 5 meters per grid slot

	apply_turn1_incidents(race_weekend_model, order_after_turn1)
	order_after_turn1 = sorted(order_after_turn1, key=lambda x: x[0], reverse=False)
	
	'''
	example of order_after_turn1
	[time_to_turn1, particpant model]
	[[12.761, <ParticpantModel Mark Webber>], [13.124, <ParticpantModel Sebastian Vettel>], [13.68, <ParticpantModel Fernando Alonso>],]
	'''
		
	return order_after_turn1

def apply_turn1_incidents(race_weekend_model: RaceWeekendModel, order_after_turn1: order_after_turn1_list) -> None:
	incident_chance = race_weekend_model.randomiser.turn1_incident_occurred()
	
	if incident_chance < TURN1_INCIDENT_CHANCE:
		spin_victim_idx = race_weekend_model.randomiser.spin_victim_idx(len(order_after_turn1))
		name = order_after_turn1[spin_victim_idx][1].name
	
		time_loss = race_weekend_model.randomiser.turn1_spin_time_loss()
		order_after_turn1[spin_victim_idx][0] += time_loss

		race_weekend_model.current_session.commentary_model.gen_turn1_spin_message(name)

	return order_after_turn1