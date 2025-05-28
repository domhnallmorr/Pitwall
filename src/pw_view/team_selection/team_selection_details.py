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

		self.engine_supplier_rating_widget = RatingWidget("Engine Supplier: Some Company", text_width=text_width)
		self.tyre_supplier_rating_widget = RatingWidget("Tyre Supplier: Some Company", text_width=text_width)

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

				ft.Text("Suppliers", weight=ft.FontWeight.BOLD, size=self.view.SUBHEADER_FONT_SIZE),
				self.engine_supplier_rating_widget,
				self.tyre_supplier_rating_widget,

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

		# image column
		self.team_logo = ft.Image(
			src=fr"{self.view.team_logos_path}\ferano.png",
			width=200,
			height=200,
			fit=ft.ImageFit.CONTAIN
		)
		
		self.team_description = ft.Text("Team Description: Some Text", no_wrap=False, expand=True,)

		image_column = ft.Column(
			controls=[
				self.team_logo, ft.Divider(), self.team_description, 
			],
			expand=True,
			tight=True,
		)

		row = ft.Row(
			controls=[
				column,
				image_column
			],
			expand=False,
			tight=True,
			alignment=ft.MainAxisAlignment.SPACE_EVENLY,
			spacing=20
		)

		self.container = CustomContainer(self.view, row)
	
	def update(self, data: TeamData) -> None:
		self.name_text.value = f"Team Name: {data["name"]}"
		self.country_text.value = f"Country: {data["country"]}"
		self.facilties_rating_widget.update_row(data["facilities"])

		self.engine_supplier_rating_widget.update_text(f"Engine Supplier: {data["engine_supplier"]}")
		self.engine_supplier_rating_widget.update_row(data["engine_supplier_overall_rating"])

		self.tyre_supplier_rating_widget.update_text(f"Tyre Supplier: {data["tyre_supplier"]}")

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

		self.image_path = fr"{self.view.team_logos_path}\{data['name'].lower()}.png"
		self.team_logo.src = self.image_path
		self.team_description.value = f"Team Description:\n{data['description']}"
		self.view.main_app.update()
