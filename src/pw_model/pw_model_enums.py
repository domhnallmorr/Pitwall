from enum import Enum


class StaffRoles(str, Enum):
	TEAM_PRINCIPAL = "team_principal"
	DRIVER1 = "driver1"
	DRIVER2 = "driver2"
	TECHNICAL_DIRECTOR = "technical_director"
	COMMERCIAL_MANAGER = "commercial_manager"


class CalendarState(Enum):
	RACE_WEEK = "race week"
	POST_RACE = "post race"
	PRE_SEASON_TESTING = "pre-season testing"
	IN_SEASON_TESTING = "in-season testing"
	POST_TEST = "post test"
	OFF_WEEK = "off week"
	PRE_SEASON = "pre-season"
	IN_SEASON = "in-season"
	POST_SEASON = "post season"

class SponsorTypes(Enum):
	NONE = "none"
	TITLE = "title sponsor"