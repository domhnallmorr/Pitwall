from __future__ import annotations
from typing import TYPE_CHECKING
import flet as ft

from pw_view.custom_widgets.custom_container import CustomContainer
from pw_view.custom_widgets.rating_widget import RatingWidget

if TYPE_CHECKING:
	from pw_view.view import View
	from pw_controller.team_selection.team_selection_controller import TeamData

class TeamSelectionDetailsContainer:
	def __init__(self, view: View):
		self.view = view
		self.setup_widgets()
		self.setup_container()

	def setup_widgets(self) -> None:
		text_width = 280 # for text widget in rating widgets

		self.name_text = ft.Text("Team Name: Some Team")
		self.country_text = ft.Text("Country: Some Country")
		self.facilties_rating_widget = RatingWidget("Facilities:", text_width=text_width)

		self.technical_director_rating_widget = RatingWidget("Technical Director: Some Lad", text_width=text_width)
		self.commercial_manager_rating_widget = RatingWidget("Commercial Manager: Some Lad", text_width=text_width)

		self.title_sponsor_text = ft.Text("Title Sponsor: Some Company")
		self.title_sponsor_value_text = ft.Text("Title Sponsor Value: $123")
		self.income_text = ft.Text("Total Income: $123")
		self.expenditure_text = ft.Text("Total Expenditure: $123")
		self.balance_text = ft.Text("Total Expenditure: $123")
		
		
		self.driver1_rating_widget = RatingWidget("Driver 1: Driver Name", text_width=text_width)
		self.driver2_rating_widget = RatingWidget("Driver 2: Driver Name", text_width=text_width)

	def setup_container(self) -> None:
		column = ft.Column(
			controls=[
				ft.Text("General", weight=ft.FontWeight.BOLD, size=self.view.SUBHEADER_FONT_SIZE),
				self.name_text,
				self.country_text,
				self.facilties_rating_widget,

				ft.Text("Senior Staff", weight=ft.FontWeight.BOLD, size=self.view.SUBHEADER_FONT_SIZE),
				self.technical_director_rating_widget,
				self.commercial_manager_rating_widget,

				ft.Text("Finances", weight=ft.FontWeight.BOLD, size=self.view.SUBHEADER_FONT_SIZE),
				self.title_sponsor_text,
				self.title_sponsor_value_text,
				self.income_text,
				self.expenditure_text,
				self.balance_text,

				ft.Text("Drivers", weight=ft.FontWeight.BOLD, size=self.view.SUBHEADER_FONT_SIZE),
				self.driver1_rating_widget,
				self.driver2_rating_widget,
			]
		)

		self.container = CustomContainer(self.view, column)
	
	def update(self, data: TeamData) -> None:
		self.name_text.value = f"Team Name: {data["name"]}"
		self.country_text.value = f"Country: {data["country"]}"
		self.facilties_rating_widget.update_row(data["facilities"])

		self.technical_director_rating_widget.update_text(f"Technical Director: {data["technical_director"]}")
		self.technical_director_rating_widget.update_row(data["technical_director_rating"])
		self.commercial_manager_rating_widget.update_text(f"Commercial Manager: {data["commercial_manager"]}")
		self.commercial_manager_rating_widget.update_row(data["commercial_manager_rating"])

		self.title_sponsor_text.value = f"Title Sponsor: {data["title_sponsor"]}"
		self.title_sponsor_value_text.value = f"Title Sponsor Value: ${data["title_sponsor_value"] :,}"
		self.income_text.value = f"Total Income: ${data["income"] :,}"
		self.expenditure_text.value = f"Total Expenditure: ${data["expenditure"] :,}"
		self.balance_text.value = f"Starting Balance: ${data["balance"] :,}"

		self.driver1_rating_widget.update_text(f"Driver 1: {data["driver1"]}")
		self.driver1_rating_widget.update_row(data["driver1_rating"])
		self.driver2_rating_widget.update_text(f"Driver 2: {data["driver2"]}")
		self.driver2_rating_widget.update_row(data["driver2_rating"])
		self.view.main_app.update()
