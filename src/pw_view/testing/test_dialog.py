from __future__ import annotations
from typing import TYPE_CHECKING
import flet as ft

if TYPE_CHECKING:
    from pw_view.view import View

class TestDialog(ft.AlertDialog):
    def __init__(self, view: View):
        self.view = view
        self.min_km = 50
        self.max_km = 1000
        self.current_km = 200  # Default starting value
        
        self.attend_test_checkbox = ft.Checkbox(
            label="Attend Test Session",
            value=True,
            on_change=self.on_checkbox_change
        )

        self.km_text = ft.Text(f"{self.current_km} km", width=100, text_align=ft.TextAlign.CENTER)
        self.decrease_km_btn = ft.IconButton(
            icon=ft.Icons.REMOVE,
            on_click=self.decrease_km,
            data=50  # Step size
        )
        self.increase_km_btn = ft.IconButton(
            icon=ft.Icons.ADD,
            on_click=self.increase_km,
            data=50  # Step size
        )

        self.km_row = ft.Row(
            controls=[
                ft.Text("Distance to run:", width=120),
                self.decrease_km_btn,
                self.km_text,
                self.increase_km_btn,
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )

        super().__init__(
            modal=True,
            title=ft.Text("Test Session Options"),
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("Configure your test session:"),
                        self.attend_test_checkbox,
                        self.km_row,
                    ],
                    spacing=10,
                    tight=True
                ),
                padding=20,
                width=400,  # Increased width to accommodate new controls
                height=150,  # Increased height to accommodate new controls
            ),
            actions=[
                ft.TextButton("Confirm", on_click=self.on_confirm),
                ft.TextButton("Cancel", on_click=self.on_cancel),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

    def increase_km(self, e):
        if self.current_km + e.control.data <= self.max_km:
            self.current_km += e.control.data
            self.update_km_controls()

    def decrease_km(self, e):
        if self.current_km - e.control.data >= self.min_km:
            self.current_km -= e.control.data
            self.update_km_controls()

    def update_km_controls(self):
        self.km_text.value = f"{self.current_km} km"
        self.decrease_km_btn.disabled = self.current_km <= self.min_km or not self.attend_test_checkbox.value
        self.increase_km_btn.disabled = self.current_km >= self.max_km or not self.attend_test_checkbox.value
        self.view.main_app.update()

    def on_checkbox_change(self, e):
        self.km_row.visible = e.control.value
        self.update_km_controls()
        self.view.main_app.update()

    def on_confirm(self, e):
        self.view.controller.testing_controller.confirm_test_options(
            attend_test=self.attend_test_checkbox.value,
            distance_km=self.current_km if self.attend_test_checkbox.value else 0
        )
        self.close_dialog()

    def on_cancel(self, e):
        self.close_dialog()

    def close_dialog(self):
        self.open = False
        self.view.main_app.update()

