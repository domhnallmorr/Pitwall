from __future__ import annotations
from typing import TYPE_CHECKING
import flet as ft

if TYPE_CHECKING:
	from pw_view.view import View

CarSpeeds = list[tuple[str, int]]

class CarComparisonGraph(ft.Column): # type: ignore
	def __init__(self, view: View):

		self.view = view

		super().__init__(expand=False,
			tight=True,
			spacing=20)

	def setup_rows(self, car_speeds: CarSpeeds) -> None:
		car_speed_rows = []

		for team in car_speeds:
			team_name = team[0]
			speed = team[1]
			
			# Note, at V0.11.0, flet version for updated to V0.25.1, the progress bar had to be put in a container 
			# in order for the bar_height property to be respected (was showing with default height)
			row = ft.Row(
				controls=[
					ft.Text(f"{team_name}:", width=100,),
					ft.Container(
						content=ft.ProgressBar(value=speed/100, width=500, expand=True, bar_height=28),
						height=28,
						expand=True
					)
				],
				expand=False,
			)
			car_speed_rows.append(row)

		self.controls = car_speed_rows
