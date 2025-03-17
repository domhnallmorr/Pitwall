from __future__ import annotations
from typing import TYPE_CHECKING
import flet as ft

from pw_view.custom_widgets.custom_container import CustomContainer
from pw_view.custom_widgets.rating_widget import RatingWidget

if TYPE_CHECKING:
    from pw_view.view import View
    from pw_controller.car_development.car_page_data import CarPageData

class EngineTab(ft.Column):
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
        self.supplier_name = ft.Text("Engine Supplier: Unknown")
        self.supplier_deal = ft.Text("Engine Supplier Deal: Unknown")
        self.power_rating = RatingWidget("Power:", text_width=text_width)
        self.resources_rating = RatingWidget("Resources:", text_width=text_width)
        self.overall_rating = RatingWidget("Overall:", text_width=text_width)

    def setup_container(self) -> None:
        controls = [
            ft.Text("Engine Details", weight=ft.FontWeight.BOLD, size=self.view.SUBHEADER_FONT_SIZE),
            self.supplier_name,
            self.supplier_deal,
            ft.Divider(),
            ft.Text("Ratings", weight=ft.FontWeight.BOLD, size=self.view.SUBHEADER_FONT_SIZE),
            self.power_rating,
            self.resources_rating,
            self.overall_rating
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
        self.supplier_name.value = f"Engine Supplier: {data.engine_supplier_name}"
        self.supplier_deal.value = f"Engine Supplier Deal: {data.engine_supplier_deal.capitalize()}"
        self.power_rating.update_row(data.engine_power)
        self.resources_rating.update_row(data.engine_resources)
        self.overall_rating.update_row(data.engine_overall_rating)