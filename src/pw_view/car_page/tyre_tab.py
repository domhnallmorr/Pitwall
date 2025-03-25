from __future__ import annotations
from typing import TYPE_CHECKING
import flet as ft

from pw_view.custom_widgets.custom_container import CustomContainer
from pw_view.custom_widgets.rating_widget import RatingWidget

if TYPE_CHECKING:
	from pw_view.view import View
	from pw_controller.car_development.car_page_data import CarPageData

class TyreTab(ft.Column):
	def __init__(self, view: View):
		self.view = view
		self.setup_widgets()
		self.setup_container()

		super().__init__(
			controls=[self.container],
			expand=False,
			tight=True,
			spacing=20
		)

	def setup_widgets(self) -> None:
		text_width = 140
		self.supplier_name = ft.Text("Tyre Supplier: Unknown")
		self.supplier_deal = ft.Text("Tyre Supplier Deal: Unknown") # Changed from deal to tyre_supplier_deal
		self.grip_rating = RatingWidget("Grip:", text_width=text_width)
		self.wear_rating = RatingWidget("Wear:", text_width=text_width)

	def setup_container(self) -> None:
		controls = [
			ft.Text("Tyre Details", weight=ft.FontWeight.BOLD, size=self.view.SUBHEADER_FONT_SIZE),
			self.supplier_name,
			self.supplier_deal, # Changed from deal to tyre_supplier_deal
			ft.Divider(), # divider causes container to stretch full width of page
			ft.Text("Ratings", weight=ft.FontWeight.BOLD, size=self.view.SUBHEADER_FONT_SIZE),
			self.grip_rating,
			self.wear_rating,
		]

		self.container = CustomContainer(
			self.view,
			ft.Column(
				controls=controls,
				expand=False,
				tight=True,
				spacing=20
			),
			expand=False
		)

	def update_tab(self, data: CarPageData) -> None:
		self.supplier_name.value = f"Tyre Supplier: {data.tyre_supplier_name}"
		self.supplier_deal.value = f"Tyre Supplier Deal: {data.tyre_supplier_deal.capitalize()}" # Changed from deal to tyre_supplier_deal
		self.grip_rating.update_row(data.tyre_grip)
		self.wear_rating.update_row(data.tyre_wear)

		self.view.main_app.update()
