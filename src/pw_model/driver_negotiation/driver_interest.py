'''
Function(s) to determine a driver's interest in joining the player's team
'''
from __future__ import annotations
from typing import TYPE_CHECKING
from enum import Enum
import random

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model

class DriverInterest(Enum):
	VERY_INTERESTED = "Very interested"
	NOT_INTERESTED = "Not interested"

def determine_driver_interest(model: Model, driver: str) -> DriverInterest:
	return random.choice(list(DriverInterest))
