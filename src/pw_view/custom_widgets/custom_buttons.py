from typing import Callable, Optional
import flet as ft

from pw_view.custom_widgets import custom_container

def gen_continue_btn(view, text: str="Continue",  on_click_func: Optional[Callable]=None) -> ft.TextButton:
	btn = ft.TextButton(text, width=200, icon="play_arrow", on_click=on_click_func)
	btn.style = view.positive_button_style

	return btn

def buttons_row(view, buttons: list) -> ft.Container:

	row = ft.Row(
			controls=buttons,
			expand=False,
			tight=True
		)
	
	return custom_container.CustomContainer(view, row, expand=False)
