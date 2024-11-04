import flet as ft

class CustomContainer(ft.Container):
	def __init__(self, view, content, expand=True, width=None):

		super(CustomContainer, self).__init__(
				content=content,
				# bgcolor=view.dark_grey,
				bgcolor=ft.colors.with_opacity(0.75, view.dark_grey),
				margin=10,
				padding=10,
				width=width,
				expand=expand,
				border_radius=15,
				shadow=ft.BoxShadow(color=ft.colors.BLACK45, blur_radius=10, spread_radius=2)
			)
