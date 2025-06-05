
from __future__ import annotations
from typing import TYPE_CHECKING
from dataclasses import dataclass
import io
import base64

from PIL import Image, ImageDraw

from pw_view.helper_functions.image_functions import get_image_bytes, hex_to_rgb, image_to_base64, recolor

if TYPE_CHECKING:
	from pw_view.view import View

@dataclass
class CarProfileData:
	team: str
	primary_colour: str
	title_sponsor: str


class CarProfileManager:
	def __init__(self, view: View):
		self.view = view

		self.car_profiles = {}
		self.side_bdy = fr"{self.view.run_directory}\pw_view\assets\car_profile\side_body.png"
		self.tyre_img = Image.open(fr"{self.view.run_directory}\pw_view\assets\car_profile\tyre.png").convert("RGBA")
		self.rear_wing = fr"{self.view.run_directory}\pw_view\assets\car_profile\rear_wing.png"
		self.front_wing = fr"{self.view.run_directory}\pw_view\assets\car_profile\front_wing.png"
		self.sidepod = fr"{self.view.run_directory}\pw_view\assets\car_profile\sidepod.png"
		self.sidepod_opening_img = Image.open(fr"{self.view.run_directory}\pw_view\assets\car_profile\sidepod_opening.png").convert("RGBA")
		self.target_color = "#8D3A3A"

	def create_car_profiles(self, data: list[CarProfileData]) -> None:
		for profile in data:
			team = profile.team
			primary_colour = profile.primary_colour
			title_sponsor = profile.title_sponsor

			self.car_profiles[team] = self.create_car_profile(team, primary_colour, title_sponsor)

	def create_car_profile(self, team: str, primary_colour: str, title_sponsor: str) -> None:
		body = Image.open(self.side_bdy).convert("RGBA")
		recolored = recolor(body, hex_to_rgb(self.target_color), hex_to_rgb(primary_colour))

		rear_wing = Image.open(self.rear_wing).convert("RGBA")
		final_image = self.add_rear_wing(rear_wing, recolored, primary_colour)

		front_wing = Image.open(self.front_wing).convert("RGBA")
		final_image = self.add_front_wing(front_wing, final_image, primary_colour)

		sidepod = Image.open(self.sidepod).convert("RGBA")
		final_image = self.add_sidepod(sidepod, final_image)

		final_image = self.add_title_sponsor(final_image, title_sponsor)

		final_image = self.add_tyres(recolored)
		final_image = self.add_sidepod_opening(final_image)

		final_image = self.add_team_logo(final_image, team)

		return final_image

	def add_front_wing(self, front_wing: Image.Image, base_img: Image.Image, primary_colour: str) -> Image.Image:
		colored_wing = recolor(front_wing, hex_to_rgb(self.target_color), hex_to_rgb(primary_colour))
		base_img.paste(colored_wing, (1085, 240), colored_wing)  # Use alpha channel as mask
		return base_img

	def add_rear_wing(self, rear_wing: Image.Image, base_img: Image.Image, primary_colour: str) -> Image.Image:
		colored_wing = recolor(rear_wing, hex_to_rgb(self.target_color), hex_to_rgb(primary_colour))
		base_img.paste(colored_wing, (1, 110), colored_wing)  # Use alpha channel as mask
		return base_img
	
	def add_sidepod(self, sidepod: Image.Image, base_img: Image.Image) -> Image.Image:
		base_img.paste(sidepod, (333, 190), sidepod)  # Use alpha channel as mask
		return base_img

	def add_tyres(self, base_img: Image.Image) -> Image.Image:
		# You can tweak these positions as needed
		positions = [(33, 160), (880, 160)]
		
		for x, y in positions:
			base_img.paste(self.tyre_img, (x, y), self.tyre_img)  # Use alpha channel as mask
		return base_img
	
	def add_sidepod_opening(self, base_img: Image.Image) -> Image.Image:
		base_img.paste(self.sidepod_opening_img, (660, 200), self.sidepod_opening_img)  # Use alpha channel as mask
		return base_img

	def add_team_logo(self, base_img: Image.Image, team: str):
		image_path = fr"{self.view.team_logos_path}\{team}.png"
		team_logo = Image.open(image_path).convert("RGBA")
		
		max_size = (70, 70)
		team_logo.thumbnail(max_size)
		base_img.paste(team_logo, (780, 190), team_logo)  # Use alpha channel as mask
		return base_img

	def add_title_sponsor(self, base_img: Image.Image, title_sponsor: str):
		image_path = fr"{self.view.sidepod_logos_path}\{title_sponsor.lower()}.png"
		title_sponsor_logo = Image.open(image_path).convert("RGBA")
		
		max_size = (350, 100)
		title_sponsor_logo.thumbnail(max_size)
		size = title_sponsor_logo.size

		width_delta = 350 - size[0]
		base_img.paste(title_sponsor_logo, (300 + width_delta//2, 230), title_sponsor_logo)  # Use alpha channel as mask
		return base_img

	def get_team_car_profile_as_base64(self, team: str) -> str:
		return image_to_base64(self.car_profiles[team])