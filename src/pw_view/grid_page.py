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

    def update_page(self, year: int, grid_this_year_df: pd.DataFrame, grid_next_year_announced_df: pd.DataFrame,
                    sponsors_this_year_df: pd.DataFrame, sponsors_next_year_df: pd.DataFrame) -> None:
        # Update tab labels
        self.current_year_tab.text = str(year)
        self.next_year_tab.text = str(year + 1)

        # Create filter buttons
        button_width = 150
        self.staff_button_container = ft.Container(
            content=ft.TextButton(
                text="Staff",
                style=ft.ButtonStyle(color=ft.Colors.WHITE),
                on_click=lambda _: self.show_staff_grid(),
                width=button_width
            ),
            border=ft.border.all(2, ft.Colors.PRIMARY),  # Initial active state
            data="active"
        )

        self.sponsor_button_container = ft.Container(
            content=ft.TextButton(
                text="Sponsors",
                style=ft.ButtonStyle(color=ft.Colors.WHITE70),
                on_click=lambda _: self.show_sponsor_grid(),
                width=button_width
            ),
            border=None,
            data="inactive"
        )

        self.filter_buttons = ft.Row(
            controls=[
                self.staff_button_container,
                self.sponsor_button_container,
            ],
            alignment=ft.MainAxisAlignment.START
        )

        # Store the data
        self.grid_this_year_df = grid_this_year_df
        self.grid_next_year_announced_df = grid_next_year_announced_df
        self.sponsors_this_year_df = sponsors_this_year_df
        self.sponsors_next_year_df = sponsors_next_year_df
        self.team_names = self.grid_this_year_df["team"].values.tolist()

        # Show staff grid by default
        self.show_staff_grid()

    def show_staff_grid(self) -> None:
        # Update button styles
        self.staff_button_container.border = ft.border.all(2, ft.Colors.PRIMARY)
        self.staff_button_container.content.style.color = ft.Colors.WHITE
        self.staff_button_container.data = "active"
        
        self.sponsor_button_container.border = None
        self.sponsor_button_container.content.style.color = ft.Colors.WHITE70
        self.sponsor_button_container.data = "inactive"

        # THIS YEAR
        self.grid_this_year_table = CustomDataTable(self.view, self.grid_this_year_df.columns.tolist(), row_height=60)
        self.grid_this_year_table.update_table_data(self.grid_this_year_df.values.tolist(),
                                                    team_logo_col_idx=0, team_logos=self.team_names)
        
        # NEXT YEAR
        self.grid_next_year_table = CustomDataTable(self.view, self.grid_next_year_announced_df.columns.tolist(), row_height=60)
        self.grid_next_year_table.update_table_data(self.grid_next_year_announced_df.values.tolist())

        self.update_tab_content()

    def show_sponsor_grid(self) -> None:
        # Update button styles
        self.sponsor_button_container.border = ft.border.all(2, ft.Colors.PRIMARY)
        self.sponsor_button_container.content.style.color = ft.Colors.WHITE
        self.sponsor_button_container.data = "active"
        
        self.staff_button_container.border = None
        self.staff_button_container.content.style.color = ft.Colors.WHITE70
        self.staff_button_container.data = "inactive"

        # THIS YEAR
        self.grid_this_year_table = CustomDataTable(self.view, self.sponsors_this_year_df.columns.tolist(), row_height=60)
        self.grid_this_year_table.update_table_data(self.sponsors_this_year_df.values.tolist())
        
        # NEXT YEAR
        self.grid_next_year_table = CustomDataTable(self.view, self.sponsors_next_year_df.columns.tolist(), row_height=60)
        self.grid_next_year_table.update_table_data(self.sponsors_next_year_df.values.tolist())

        self.update_tab_content()

    def update_tab_content(self) -> None:
        content_column = ft.Column(
            controls=[
                ft.Container(
                    content=self.filter_buttons,
                    padding=ft.padding.only(left=20, top=20, bottom=10)  # Added top and bottom padding
                ),
                self.grid_this_year_table.list_view
            ],
            expand=True
        )

        next_year_content_column = ft.Column(
            controls=[
                ft.Container(
                    content=self.filter_buttons,
                    padding=ft.padding.only(left=20, top=20, bottom=10)  # Added top and bottom padding
                ),
                self.grid_next_year_table.list_view
            ],
            expand=True
        )

        self.current_year_tab.content.content = content_column
        self.next_year_tab.content.content = next_year_content_column
        
        self.view.main_app.update()
