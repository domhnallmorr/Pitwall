from enum import Enum


class StaffRoles(str, Enum):
	TEAM_PRINCIPAL = "team_principal"
	DRIVER1 = "driver1"
	DRIVER2 = "driver2"
	TECHNICAL_DIRECTOR = "technical_director"
	COMMERCIAL_MANAGER = "commercial_manager"
