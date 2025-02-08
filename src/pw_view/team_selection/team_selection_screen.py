from __future__ import annotations

from typing import TYPE_CHECKING
import flet as ft

from pw_view.team_selection.team_selection_details import TeamSelectionDetailsContainer
from pw_view.custom_widgets.custom_container import CustomContainer, HeaderContainer
from pw_view.custom_widgets.custom_buttons import gen_continue_btn, buttons_row

if TYPE_CHECKING:
	from pw_view.view import View

class TeamSelectionScreen(ft.View): # type: ignore
    def __init__(self, view: View, team_names: list[str]):
        self.view = view
        self.team_names = team_names
        self.selected_team = team_names[0]
        
        # Create team buttons
        self.team_buttons = [
            # ft.ElevatedButton(name, data=name, on_click=self.update_team_details, width=200)
            ft.ListTile(title=ft.Text(name, color=view.dark_grey, weight="bold"),
                        data=name, on_click=self.update_team_details, bgcolor=ft.Colors.GREY)
            for name in team_names
        ]

        self.team_buttons[0].bgcolor = ft.Colors.PRIMARY # set first button selected color

        # Team selection container
        team_selection_container = CustomContainer(
            view=view,
            content=
                ft.Column(self.team_buttons, alignment=ft.MainAxisAlignment.START),
            expand=False,
            width=250  # Keeps it narrow on the left,
        )

        self.teams_details_container = TeamSelectionDetailsContainer(self.view)

        # Start Career Button (Bottom Left)
        start_career_button = gen_continue_btn(self.view, "Start Career", on_click_func=self.start_career)
        start_career_row = buttons_row(view, [start_career_button])

        # Layout
        layout = ft.Column(
            [
                # ft.Text("Team Selection", theme_style=self.view.page_header_style),
				ft.Row([team_selection_container, self.teams_details_container.container], expand=True),
                start_career_row  # Puts button at bottom
            ],
            expand=True
        )

        self.background_stack = ft.Stack(
			[
				# Add the resizable background image
				self.view.background_image,
				layout,
			],
			expand=True,  # Make sure the stack expands to fill the window
		)

        controls = [
					ft.Text("Team Selection", theme_style=self.view.page_header_style),
					self.background_stack
		]

        super().__init__(controls=controls)

    def update_team_details(self, e: ft.ControlEvent) -> None:
        """Updates the team details container when a team is selected."""
        # reset color of previously selected team
        self.team_buttons[self.team_names.index(self.selected_team)].bgcolor = ft.Colors.GREY

        self.selected_team = e.control.data
        self.team_buttons[self.team_names.index(self.selected_team)].bgcolor = ft.Colors.PRIMARY
        self.view.controller.team_selection_controller.team_selected(self.selected_team)

    def start_career(self, e: ft.ControlEvent) -> None:
        self.view.controller.start_career(self.selected_team)
