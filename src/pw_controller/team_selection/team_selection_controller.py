
'''
Controller to handle team selection page
'''
from __future__ import annotations
from typing import TYPE_CHECKING, TypedDict, Optional

from pw_model.team.team_facade import get_team_title_sponsor, get_team_title_sponsor_value, get_facilities_rating
from pw_model.team.team_facade import get_team_income, get_team_expenditure, get_team_balance

if TYPE_CHECKING:
	from pw_controller.pw_controller import Controller
	from pw_model.pw_base_model import Model


class TeamSelectionController:
	def __init__(self, controller: Controller):
		self.controller = controller
	
	@property
	def model(self) -> Model:
		return self.controller.model
	
	def setup_default_team(self) -> None:
		'''
		update the team selection page to show the first teams details by default
		'''
		team = self.model.teams[0].name
		self.team_selected(team)

	def team_selected(self, team: str) -> None:
		team_model = self.model.get_team_model(team)

		data : TeamData = {
			"name": team,
			"country": team_model.country,
			"facilities": get_facilities_rating(team_model),

			"technical_director": team_model.technical_director,
			"technical_director_rating": team_model.technical_director_model.average_skill,
			"commercial_manager": team_model.commercial_manager,
			"commercial_manager_rating": team_model.commercial_manager_model.average_skill,
			"engine_supplier": team_model.engine_supplier_model.name,
			"engine_supplier_overall_rating": team_model.engine_supplier_model.overall_rating,

			"title_sponsor": get_team_title_sponsor(team_model),
			"title_sponsor_value": get_team_title_sponsor_value(team_model),
			"income": get_team_income(team_model),
			"expenditure": get_team_expenditure(team_model),
			"balance": get_team_balance(team_model),

			"driver1": team_model.driver1,
			"driver1_rating": team_model.driver1_model.overall_rating,
			"driver2": team_model.driver2,
			"driver2_rating": team_model.driver2_model.overall_rating
		}

		self.controller.view.team_selection_screen.teams_details_container.update(data)

class TeamData(TypedDict):
	name: str
	country: str
	facilities: int

	technical_director: str
	technical_director_rating: int
	commercial_manager: str
	commercial_manager_rating: int
	engine_supplier: str
	engine_supplier_overall_rating: int

	title_sponsor: str
	title_sponsor_value: int
	income: int
	expenditure: int
	balance: int

	driver1: str
	driver1_rating: int
	driver2: str
	driver2_rating: int