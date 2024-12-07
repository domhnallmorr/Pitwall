import flet as ft

from typing import Optional

class WorkforceDialog(ft.AlertDialog):
    def __init__(self, page: ft.Page, view, initial_value: int, on_apply=None):
        super().__init__(
            modal=True, 
            title=ft.Text("Adjust Workforce")
        )
        
        self.page = page
        self.view = view
        self.initial_value = initial_value
        self.on_apply = on_apply
        self.workforce_input = ft.TextField(label="Number of Staff", value=str(initial_value), width=150, read_only=True)
        
        # Increase and Decrease buttons
        self.increase_button = ft.ElevatedButton("Increase", on_click=self.increase_workforce)
        self.decrease_button = ft.ElevatedButton("Decrease", on_click=self.decrease_workforce)
        
        # Use a container to limit the dialog's size
        self.content = ft.Container(
            content=ft.Column(
                [
                    self.workforce_input,
                    ft.Row([self.increase_button, self.decrease_button], alignment=ft.MainAxisAlignment.CENTER)
                ],
                alignment=ft.MainAxisAlignment.CENTER,  # Center items vertically
                horizontal_alignment=ft.CrossAxisAlignment.CENTER  # Center items horizontally
            ),
            padding=20,  # Optional: Add padding for compact look
            width=300,   # Set container width
            height=200,  # Set container height for compactness
            alignment=ft.alignment.center  # Center the content within the dialog
        )
        
        # Dialog action buttons
        self.actions = [
           ft.TextButton("Apply", on_click=self.apply_changes),
           ft.TextButton("Cancel", on_click=self.close_dialog),
        ]

        self.enable_disable_buttons()
    
    def increase_workforce(self, e: ft.ControlEvent) -> None:
        # Increase the workforce input by 1
        self.workforce_input.value = str(int(self.workforce_input.value) + 1)
        self.enable_disable_buttons()
        self.page.update()
    
    def decrease_workforce(self, e: ft.ControlEvent) -> None:
        # Decrease the workforce input by 1
        self.workforce_input.value = str(int(self.workforce_input.value) - 1)
        self.enable_disable_buttons()
        self.page.update()
    
    def apply_changes(self, e: ft.ControlEvent) -> None:
        # Apply changes and close dialog
        new_workforce = int(self.workforce_input.value)

        self.view.controller.staff_hire_controller.update_workforce(new_workforce)
        self.close_dialog(None)
            
    def enable_disable_buttons(self) -> None:
        self.decrease_button.disabled = False
        self.increase_button.disabled = False

        if int(self.workforce_input.value) == 90:
            self.decrease_button.disabled = True
        elif int(self.workforce_input.value) == 250:
            self.increase_button.disabled = True

        # limit change to no more than 20 increase or decrease in a season
        elif int(self.workforce_input.value) - self.initial_value >= 20:
            self.increase_button.disabled = True
        elif int(self.workforce_input.value) - self.initial_value <= -20:
            self.decrease_button.disabled = True

        self.page.update()    
            
    def close_dialog(self, e: Optional[ft.ControlEvent]) -> None:
        self.open = False
        self.page.update()
