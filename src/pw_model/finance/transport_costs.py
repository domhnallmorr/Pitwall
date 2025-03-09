'''
1. Estimate transport costs at the start of each season
2. Calculate transport costs across the season
'''

from __future__ import annotations
from typing import TYPE_CHECKING
from enum import Enum
import random

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model

class TransportCostsModel:
	def __init__(self, model: Model):
		self.model = model
		self.randomiser = TransportCostsRandomiser()

		self.setup_country_costs()
		
	def setup_new_season(self) -> None:
		self.estimate_season_transport_costs()
		self.total_costs = 0
		self.costs_by_race: list[int] = []

	def estimate_season_transport_costs(self) -> None:
		self.estimated_season_costs = 0

		for country in self.model.season.calendar.countries:
			self.estimated_season_costs += self.get_country_costs(country)
	
	def gen_race_transport_cost(self) -> None:
		country = self.model.season.calendar.current_track_model.country
		cost = self.get_country_costs(country) + self.randomiser.gen_random_element_of_transport_cost()
		self.total_costs += cost
		self.costs_by_race.append(cost)

	def setup_country_costs(self) -> None:
		self.country_costs = {
			"Australia": TransportCosts.MAX,
			"Brazil": TransportCosts.HIGH,
			"Argentina": TransportCosts.HIGH,
			"San Marino": TransportCosts.LOW,  # Italy
			"Spain": TransportCosts.MEDIUM,
			"Monaco": TransportCosts.LOW,
			"Canada": TransportCosts.HIGH,
			"France": TransportCosts.LOW,
			"United Kingdom": TransportCosts.LOW,
			"Austria": TransportCosts.MEDIUM,
			"Germany": TransportCosts.LOW,
			"Hungary": TransportCosts.MEDIUM,
			"Belgium": TransportCosts.LOW,
			"Italy": TransportCosts.LOW,
			"Luxembourg": TransportCosts.MEDIUM,  # Nürburgring, Germany
			"Japan": TransportCosts.MAX
		}

	def get_country_costs(self, country: str) -> int:
		if country in self.country_costs.keys():
			return self.country_costs[country].value
		else:
			return TransportCosts.MEDIUM.value


class TransportCosts(Enum):
	LOW = 140_000
	MEDIUM = 240_000
	HIGH = 340_000
	MAX = 440_000

class TransportCostsRandomiser:
	def gen_random_element_of_transport_cost(self) -> int:
		return random.randint(-30_000, 80_000)
	