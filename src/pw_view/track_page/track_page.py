from __future__ import annotations
from typing import TYPE_CHECKING

import flet as ft

from pw_view.custom_widgets.custom_container import CustomContainer
from pw_view.custom_widgets.rating_widget import RatingWidget

if TYPE_CHECKING:
	from pw_view.view import View
	from pw_controller.track_page.track_page_data import TrackData

class TrackPage(ft.Column): # type: ignore
	def __init__(self, view: View):
		self.view = view

		self.setup_widgets()
		self.setup_page()

		contents = [
			ft.Text("Track", theme_style=self.view.page_header_style),
			self.background_stack,
		]

		super().__init__(expand=1, controls=contents)

	def setup_page(self) -> None:
		details_column = ft.Column(
			controls=[ft.Text("Track Details", weight=ft.FontWeight.BOLD, size=self.view.SUBHEADER_FONT_SIZE,),
				self.name_text, self.length_text, self.laps_text, self.overtaking_difficulty_rating], 
			expand=False, tight=True, alignment=ft.alignment.top_left)
		
		self.track_map = ft.Image(
                                src=fr"C:\Users\domhn\Documents\python\Pitwall\src\pw_view\assets\track_maps\Albert Park.png",
		)
		map_column = ft.Column(
			controls=[ft.Text("Track Map", weight=ft.FontWeight.BOLD, size=self.view.SUBHEADER_FONT_SIZE,),
			 self.track_map],
			 expand=False, tight=True, expand_loose=False,)# alignment=ft.MainAxisAlignment.START
			#  )

		details_container = CustomContainer(self.view, content=details_column, expand=False)
		map_container = CustomContainer(self.view, content=map_column, expand=False)

		layout = ft.Row(controls=[details_container, map_container],
				  expand=False, tight=True)
		
		self.background_stack : ft.Stack = ft.Stack(
			[
				# Add the resizable background image
				self.view.background_image,
				layout,
			],
			expand=True,  # Make sure the stack expands to fill the window
		)

	def setup_widgets(self) -> None:
		self.name_text = ft.Text("Name: Some Track")
		self.length_text = ft.Text("Length: 9.9km")
		self.laps_text = ft.Text("Laps: 99")
		self.overtaking_difficulty_rating = RatingWidget("Overtaking Difficulty", min_value=600, max_value=1_800)

	def update_page(self, data: TrackData) -> None:
		self.name_text.value = f"Name: {data.name}"
		self.length_text.value = f"Length: {data.length}km"
		self.laps_text.value = f"Laps: {data.laps}km"
		self.overtaking_difficulty_rating.update_row(data.overtaking_delta)

		self.track_map.src = fr"{self.view.track_maps_path}\{data.name}.png"
		
		self.view.main_app.update()