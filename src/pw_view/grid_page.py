from __future__ import annotations
from typing import TYPE_CHECKING
import flet as ft
import pandas as pd
from pw_view.custom_widgets import custom_container
from pw_view.custom_widgets.custom_datatable import CustomDataTable

if TYPE_CHECKING:
    from pw_view.view import View

class GridPage(ft.Column):
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
                ft.Text("Grid", theme_style=self.view.page_header_style),
                self.background_stack
            ],
            alignment=ft.MainAxisAlignment.START,
            expand=True
        )

    def setup_tabs(self) -> None:
        # Initialize with placeholder years that will be updated
        self.current_year_tab = ft.Tab(
            text="1998",
            content=ft.Container(
                expand=False,
                alignment=ft.alignment.top_center
            )
        )
        
        self.next_year_tab = ft.Tab(
            text="1999",
            content=ft.Container(
                expand=False,
                alignment=ft.alignment.top_center
            )
        )

        self.tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                self.current_year_tab,
                self.next_year_tab
            ],
            expand=True
        )

    def update_page(self, year: int, grid_this_year_df: pd.DataFrame, grid_next_year_announced_df: pd.DataFrame) -> None:
        # Update tab labels
        self.current_year_tab.text = str(year)
        self.next_year_tab.text = str(year + 1)

        # THIS YEAR
        self.grid_this_year_table = CustomDataTable(self.view, grid_this_year_df.columns.tolist())
        self.grid_this_year_table.update_table_data(grid_this_year_df.values.tolist())
        self.current_year_tab.content.content = self.grid_this_year_table.list_view

        # NEXT YEAR
        self.grid_next_year_table = CustomDataTable(self.view, grid_next_year_announced_df.columns.tolist())
        self.grid_next_year_table.update_table_data(grid_next_year_announced_df.values.tolist())
        self.next_year_tab.content.content = self.grid_next_year_table.list_view

        # Reset to current year view
        self.tabs.selected_index = 0
        self.view.main_app.update()
