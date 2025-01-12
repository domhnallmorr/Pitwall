from __future__ import annotations
import random
from typing import TYPE_CHECKING

import pandas as pd

from race_weekend_model.particpant_model import ParticpantModel
from race_weekend_model.race_model_enums import SessionMode

if TYPE_CHECKING:
	from race_weekend_model.race_weekend_model import RaceWeekendModel

def calculate_run_to_turn1(race_weekend_model: RaceWeekendModel) -> list[tuple[float, ParticpantModel]]:

	dist_to_turn1 = race_weekend_model.track_model.dist_to_turn1
	AVERAGE_SPEED = 47.0 #m/s

	order_after_turn1: list[tuple[float, ParticpantModel]] = []
	standings_df = race_weekend_model.current_session.standings_model.dataframe.copy(deep=True)

	for idx, p in enumerate([race_weekend_model.get_particpant_model_by_name(n) for n in standings_df["Driver"].values.tolist()]):
		random_factor = race_weekend_model.randomiser.run_to_turn1_random_factor(p.name)
		time_to_turn1: float = round(dist_to_turn1 / (AVERAGE_SPEED + random_factor), 3)
		particpant_model: ParticpantModel = p
		order_after_turn1.append((time_to_turn1, particpant_model))
		
		dist_to_turn1 += 5 # add 5 meters per grid slot

	order_after_turn1 = sorted(order_after_turn1, key=lambda x: x[0], reverse=False)
	
	'''
	example of order_after_turn1
	[time_to_turn1, particpant model]
	[[12.761, <RaceEngineParticpantModel Mark Webber>], [13.124, <RaceEngineParticpantModel Sebastian Vettel>], [13.68, <RaceEngineParticpantModel Fernando Alonso>],]
	'''
		
	return order_after_turn1