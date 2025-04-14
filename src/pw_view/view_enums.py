from enum import Enum


class ViewPageEnums(Enum):
	CALENDAR = "calendar"
	CAR = "car"
	EMAIL = "email"
	FACILITY = "facility"
	FINANCE = "finance"
	GRID = "grid"
	HOME = "home"
	STAFF = "staff"
	STANDINGS = "standings"
	TRACKPAGE = "track_page"

class AdvanceModeEnums(Enum):
	ADVANCE = "Advance"
	GO_TO_RACE = "Go To Race"
	GO_TO_TEST = "Go To Test"