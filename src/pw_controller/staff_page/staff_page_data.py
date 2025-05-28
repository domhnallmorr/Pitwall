from dataclasses import dataclass
from typing import List

from pw_model.pw_base_model import Model
from pw_model.pw_model_enums import StaffRoles

@dataclass
class StaffPlayerRequires:
     player_requiring_driver1: bool
     player_requiring_driver2: bool
     player_requiring_technical_director: bool
     player_requiring_commercial_manager: bool
     
@dataclass
class DriverData:
    name: str
    age: int
    country: str
    speed: int
    consistency: int
    qualifying: int
    contract_length: int
    salary: int
    retiring: bool
    starts: int

@dataclass
class SeniorStaffData:
    name: str
    age: int
    contract_length: int
    skill: int
    retiring: bool
    salary: int
    
@dataclass
class StaffPageData:
    drivers: List[DriverData]
    commercial_manager: SeniorStaffData
    technical_director: SeniorStaffData
    staff_values: list[tuple[str, int]]
    staff_player_requires: StaffPlayerRequires
    
def get_staff_page_data(model: Model) -> StaffPageData:
	staff_market = model.staff_market
	team_model = model.entity_manager.get_team_model(model.player_team)
	staff_values = [[team.name, team.number_of_staff] for team in model.teams]
	staff_values.sort(key=lambda x: x[1], reverse=True) # sort, highest to lowest
     
	data = StaffPageData(
		drivers=[
			DriverData(
				name=team_model.driver1_model.name,
				age=team_model.driver1_model.age,
				country=team_model.driver1_model.country,
				speed=team_model.driver1_model.speed,
				consistency=team_model.driver1_model.consistency,
				qualifying=team_model.driver1_model.qualifying,
				contract_length=team_model.driver1_model.contract.contract_length,
				salary=team_model.driver1_model.contract.salary,
				retiring=team_model.driver1_model.retiring,
				starts=team_model.driver1_model.career_stats.starts,
			),
			DriverData(
				name=team_model.driver2_model.name,
				age=team_model.driver2_model.age,
				country=team_model.driver2_model.country,
				speed=team_model.driver2_model.speed,
				consistency=team_model.driver2_model.consistency,
				qualifying=team_model.driver2_model.qualifying,
				contract_length=team_model.driver2_model.contract.contract_length,
				salary=team_model.driver2_model.contract.salary,
				retiring=team_model.driver2_model.retiring,
				starts=team_model.driver2_model.career_stats.starts,
			),
		],
		commercial_manager=SeniorStaffData(
			name=team_model.commercial_manager_model.name,
			age=team_model.commercial_manager_model.age,
			contract_length=team_model.commercial_manager_model.contract.contract_length,
			skill=team_model.commercial_manager_model.skill,
            retiring=team_model.commercial_manager_model.retiring,
            salary=team_model.commercial_manager_model.contract.salary
		),
          
		technical_director=SeniorStaffData(
			name=team_model.technical_director,
			age=team_model.technical_director_model.age,
			contract_length=team_model.technical_director_model.contract.contract_length,
			skill=team_model.technical_director_model.skill,
            retiring=team_model.technical_director_model.retiring,
            salary=team_model.technical_director_model.contract.salary
		),
          
		staff_values=staff_values,
        
		staff_player_requires=StaffPlayerRequires(
               player_requiring_driver1=staff_market.player_requiring_driver1,
               player_requiring_driver2=staff_market.player_requiring_driver2,
               player_requiring_technical_director=staff_market.player_requiring_technical_director,
               player_requiring_commercial_manager=staff_market.player_requiring_commercial_manager,
		)
	)

	return data