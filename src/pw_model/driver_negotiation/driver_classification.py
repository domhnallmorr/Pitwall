from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model

from pw_model.driver_negotiation.driver_negotiation_enums import DriverCategory


def classify_driver(driver: str, model: Model) -> DriverCategory:
	driver_model = model.entity_manager.get_driver_model(driver)
	rating = driver_model.overall_rating
	starts = driver_model.career_stats.starts

	if rating >= 90 and starts >= 40: # elite drivers must have started at least 30 races to be considered elite
		return DriverCategory.ELITE
	elif rating >= 70 and starts >= 30:
		return DriverCategory.TOP
	elif rating >= 50 and starts >= 16:
		return DriverCategory.MID
	else:
		return DriverCategory.BOTTOM