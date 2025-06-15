from __future__ import annotations
from typing import TYPE_CHECKING
import flet as ft

from pw_view.custom_widgets import custom_datatable
from pw_view.custom_widgets.results_table import DriverResultsTable
from pw_view.custom_widgets.custom_container import CustomContainer, HeaderContainer
from pw_view.custom_widgets.rating_widget import RatingWidget
from pw_controller.driver_page.driver_page_data import DriverPageData

if TYPE_CHECKING:
    from pw_view.view import View


class DriverPage(ft.Column):
    def __init__(self, view: View):
        self.view = view
        self.setup_widgets()
        self.setup_personal_details()
        self.setup_career_stats()
        self.setup_layout()

        super().__init__(
            controls=[
                ft.Text("Driver", theme_style=self.view.page_header_style),
                self.background_stack,
            ],
            alignment=ft.MainAxisAlignment.START,
            expand=True,
        )

    def setup_widgets(self) -> None:
        self.name_text = ft.Text("Name: Mr X")
        self.age_text = ft.Text("Age: 0 Years")
        self.country_text = ft.Text("Country: Country")

        self.image = ft.Image(
            src=fr"{self.view.driver_images_path}\mrx.png",
            width=200,
            height=200,
            fit=ft.ImageFit.CONTAIN,
        )

        self.starts_text = ft.Text("Starts: 0")
        self.championships_text = ft.Text("Championships: 0")
        self.wins_text = ft.Text("Wins: 0")

        self.salary_text = ft.Text("Salary: $0")
        self.contract_length_text = ft.Text("Contract Length: 0 Year(s)")
        self.contract_status_text = ft.Text("Contract Status: Contracted")

        text_width = 110
        self.ability_widget = RatingWidget("Ability", text_width=text_width)
        self.speed_widget = RatingWidget("Speed:", text_width=text_width)
        self.qualifying_widget = RatingWidget(
            "Qualifying:", min_value=1, max_value=5, text_width=text_width
        )
        self.consistency_widget = RatingWidget("Consistency:", text_width=text_width)

        #TODO update number of columns to be dynamic
        # self.race_results_table = custom_datatable.CustomDataTable(self.view, [str(i) for i in range(16)])
        self.results_table = DriverResultsTable(self.view)

    def setup_personal_details(self) -> None:
        controls = [
            ft.Text("Personal Details", weight=ft.FontWeight.BOLD, size=self.view.SUBHEADER_FONT_SIZE,),
            self.name_text,
            self.age_text,
            self.country_text,
        ]

        col1 = ft.Column(controls=controls, expand=False)
        col2 = ft.Column(controls=[self.image], expand=False)

        self.personal_details_row = ft.Row(controls=[col1, col2], expand=False, tight=True, alignment=ft.MainAxisAlignment.CENTER,
                                           vertical_alignment=ft.CrossAxisAlignment.START, spacing=100)


    def setup_career_stats(self) -> None:
        controls = [
            ft.Text("Career Stats", weight=ft.FontWeight.BOLD, size=self.view.SUBHEADER_FONT_SIZE,),
            self.starts_text,
            self.championships_text,
            self.wins_text,
        ]

        self.career_stats_column = ft.Column(controls=controls, expand=True, alignment=ft.MainAxisAlignment.START)

    def setup_layout(self) -> None:
        # TOP ROW
        controls = [
            self.personal_details_row,
            ft.VerticalDivider(),
            self.career_stats_column,
        ]
        
        self.row1 = ft.Row(controls=controls, expand=False, tight=False, height=200,
                           alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.START,spacing=100)
        
        controls = [
            HeaderContainer(self.view, "Driver Details"),
            self.row1,
            ft.Divider(),
            ft.Text(
                "Contract",
                weight=ft.FontWeight.BOLD,
                size=self.view.SUBHEADER_FONT_SIZE,
            ),
            self.salary_text,
            self.contract_length_text,
            self.contract_status_text,
            ft.Divider(),
            ft.Text(
                "Stats",
                weight=ft.FontWeight.BOLD,
                size=self.view.SUBHEADER_FONT_SIZE,
            ),
            self.ability_widget,
            self.speed_widget,
            self.qualifying_widget,
            self.consistency_widget,
            ft.Divider(),
            ft.Text(
                "Race Results",
                weight=ft.FontWeight.BOLD,
                size=self.view.SUBHEADER_FONT_SIZE,
            ),
            self.results_table.list_view,
        ]

        column = ft.Column(controls=controls, expand=False)
        container = CustomContainer(self.view, column, expand=False)

        self.background_stack = ft.Stack(
            [self.view.background_image, container], expand=True
        )

    def update_page(self, data: DriverPageData) -> None:
        self.name_text.value = f"Name: {data.name}"
        self.age_text.value = f"Age: {data.age} Years"
        self.country_text.value = f"Country: {data.country}"

        self.image.src = fr"{self.view.driver_images_path}\{data.name.lower()}.png"

        self.starts_text.value = f"Starts: {data.starts}"
        self.championships_text.value = f"Championships: {data.championships}"
        self.wins_text.value = f"Wins: {data.wins}"
        
        self.salary_text.value = f"Salary: ${data.salary:,}"
        self.contract_length_text.value = (
            f"Contract Length: {data.contract_length} Year(s)"
        )
        if data.retiring:
            self.contract_status_text.value = "Contract Status: Retiring"
        elif data.contract_length < 2:
            self.contract_status_text.value = "Contract Status: Contract Expiring"
        else:
            self.contract_status_text.value = "Contract Status: Contracted"

        self.ability_widget.update_row(data.speed)
        self.speed_widget.update_row(data.speed)
        self.qualifying_widget.update_row(data.qualifying)
        self.consistency_widget.update_row(data.consistency)

        self.results_table.update_results(data.race_countries, data.race_results_df.values.tolist()[0])

        self.view.main_app.update()