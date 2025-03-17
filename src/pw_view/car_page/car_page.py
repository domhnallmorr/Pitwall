from __future__ import annotations
from typing import TYPE_CHECKING
import flet as ft

from pw_view.custom_widgets import custom_container
from pw_view.car_page.car_comparison_graph import CarComparisonGraph
from pw_view.car_page.car_development_tab import CarDevelopmentTab
from pw_view.car_page.engine_tab import EngineTab

if TYPE_CHECKING:
    from pw_view.view import View
    from pw_controller.car_development.car_page_data import CarPageData

class CarPage(ft.Column):
    def __init__(self, view: View):
        self.view = view
        self.setup_tabs()

        self.background_stack = ft.Stack(
            [
                self.view.background_image,
                self.tabs
            ],
            expand=True
        )

        super().__init__(
            controls=[
                ft.Text("Car", theme_style=self.view.page_header_style),
                self.background_stack
            ],
            alignment=ft.MainAxisAlignment.START,
            expand=True
        )

    def setup_tabs(self) -> None:
        self.car_development_tab = CarDevelopmentTab(self.view)
        self.car_comparison_graph = CarComparisonGraph(self.view)
        self.engine_tab = EngineTab(self.view)
        
        self.car_comparison_container = custom_container.CustomContainer(
            self.view, 
            self.car_comparison_graph, 
            expand=False
        )

        self.tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="Engine",
                    icon=ft.Icons.SETTINGS,
                    content=ft.Container(
                        content=self.engine_tab,
                        expand=False,
                        alignment=ft.alignment.top_center
                    )
                ),
                ft.Tab(
                    text="Car Development",
                    icon=ft.Icons.HARDWARE,
                    content=ft.Container(
                        content=self.car_development_tab,
                        expand=False,
                        alignment=ft.alignment.top_center
                    )
                ),
                ft.Tab(
                    text="Car Comparison",
                    icon=ft.Icons.SHOW_CHART,
                    content=ft.Container(
                        content=self.car_comparison_container,
                        expand=False,
                        alignment=ft.alignment.top_center
                    )
                ),           
            ],
            expand=True
        )

    def update_page(self, data: CarPageData) -> None:
        self.car_comparison_graph.setup_rows(data.car_speeds)
        self.car_development_tab.update_tab(data)
        self.engine_tab.update_tab(data)
        self.view.main_app.update()
