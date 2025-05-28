from __future__ import annotations
from typing import TYPE_CHECKING
import flet as ft

from pw_view.custom_widgets import custom_container
from pw_view.custom_widgets.custom_datatable import CustomDataTable

if TYPE_CHECKING:
    from pw_view.view import View

class SponsorsTab(ft.Column):
    def __init__(self, view: View):
        self.view = view
        self.setup_widgets()

        content = ft.Column(
            controls=[
                self.sponsors_table.list_view
            ],
            expand=False
        )

        super().__init__(
            controls=[content],
            expand=False
        )

    def setup_widgets(self) -> None:
        column_names = [
            "Sponsor Type",
            "Name",
            "Payment",
            "Contract Remaining"
        ]
        
        self.sponsors_table = CustomDataTable(self.view, column_names)
        # Initialize with empty data
        self.sponsors_table.update_table_data([["-", "-", "-", "-"]])

    def update_tab(self, data: dict) -> None:
        
        self.sponsors_table.update_table_data(data["summary_df"].to_numpy().tolist())
