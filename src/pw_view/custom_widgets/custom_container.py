from __future__ import annotations
from typing import TYPE_CHECKING, Optional

import flet as ft

if TYPE_CHECKING:
	from pw_view.view import View

class CustomContainer(ft.Container):
	def __init__(self, view: View, content: list, expand: bool=True, width: Optional[int]=None, height: Optional[int]=None):

		super(CustomContainer, self).__init__(
				content=content,
				# bgcolor=view.dark_grey,
				bgcolor=ft.Colors.with_opacity(0.75, view.dark_grey),
				margin=10,
				padding=10,
				width=width,
				height=height,
				expand=expand,
				border_radius=15,
				shadow=ft.BoxShadow(color=ft.Colors.BLACK45, blur_radius=10, spread_radius=2)
			)

class HeaderContainer(ft.Container):
	def __init__(self, view: View, text: str, expand: bool=True, width: Optional[int]=None):
		'''
		This is the header row at the top of a CustomContainer
		'''
		super(HeaderContainer, self).__init__(
				content=ft.Text(text, weight="bold", color=view.dark_grey, size=20),
				alignment=ft.alignment.center,
				bgcolor=ft.Colors.with_opacity(0.75, ft.Colors.PRIMARY),
				height=40,
				expand=expand,
				border_radius=ft.border_radius.only(15, 15, 0, 0)
			)

		