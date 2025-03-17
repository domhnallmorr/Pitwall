import pytest
import flet as ft
from pw_view.staff_page.hire_staff_page import HireStaffPage

# Try importing StaffRoles; if not available, create a dummy version.

from pw_model.pw_model_enums import StaffRoles


# Dummy classes to simulate the view and controller structure
class DummyWindow:
    def __init__(self, height=600):
        self.height = height

class DummyMainApp:
    def __init__(self):
        self.window = DummyWindow()
        self.overlay = []
    def update(self):
        pass
    def open(self, dialog):
        pass
    def close(self, dialog):
        if dialog in self.overlay:
            self.overlay.remove(dialog)

class DummyStaffHireController:
    def __init__(self):
        self.offers = []
        self.completions = []
    def get_staff_details(self, name, role):
        # Return dummy staff details
        return {"name": f"Test {name}", "age": "35"}
    def make_driver_offer(self, name, role):
        self.offers.append((name, role))
    def complete_hire(self, name, role):
        self.completions.append((name, role))

class DummyController:
    def __init__(self):
        self.staff_hire_controller = DummyStaffHireController()

class DummyView:
    def __init__(self):
        self.page_header_style = "header-style"
        self.dark_grey = "#333333"
        self.vscroll_buffer = 50
        self.background_image = None
        self.main_app = DummyMainApp()
        self.controller = DummyController()

# Helper classes to simulate Flet event objects
class DummyControl:
    def __init__(self, data):
        self.data = data
        self.text = ""

class DummyEvent:
    def __init__(self, data):
        self.control = DummyControl(data)

# Test updating the free agent list
def test_update_free_agent_list():
    view = DummyView()
    page = HireStaffPage(view)
    free_agents = ["Alice", "Bob"]
    role = StaffRoles.DRIVER1
    previously_approached = ["Bob"]
    page.update_free_agent_list(free_agents, role, previously_approached)
    
    # Verify that the title and current role are updated
    assert page.title_text.value == f"Hire: Driver 1"
    assert page.current_role == role
    
    # Check that two buttons were created and the disabled states are set correctly
    assert len(page.name_text_buttons) == 2
    for btn in page.name_text_buttons:
        if btn.data == "Bob":
            assert btn.disabled is True
        elif btn.data == "Alice":
            assert btn.disabled is False
            
    # update_free_agent_list automatically calls update_staff on free_agents[0]
    assert page.name_text.value == "Driver Name: Test Alice"
    assert page.age_text.value == "Driver Age: 35"

# Test the update_staff method
def test_update_staff():
    view = DummyView()
    page = HireStaffPage(view)
    page.current_role = StaffRoles.DRIVER1
    e = DummyEvent("Charlie")
    page.update_staff(e)
    
    assert page.name_text.value == "Driver Name: Test Charlie"
    assert page.age_text.value == "Driver Age: 35"
    assert page.offer_btn.data == "Charlie"
    assert page.offer_btn.disabled is False

# Test approach_staff when hiring a driver (driver roles)
def test_approach_staff_for_driver():
    view = DummyView()
    page = HireStaffPage(view)
    free_agents = ["Dave"]
    role = StaffRoles.DRIVER1
    previously_approached = []
    page.update_free_agent_list(free_agents, role, previously_approached)
    
    e = DummyEvent("Dave")
    # Ensure the offer button is enabled before the call
    page.offer_btn.disabled = False
    page.approach_staff(e)
    
    # Verify that a driver offer was made
    offers = view.controller.staff_hire_controller.offers
    assert ("Dave", role) in offers
    
    # Verify that the offer button is now disabled
    assert page.offer_btn.disabled is True
    # And the corresponding name button should be disabled too
    for btn in page.name_text_buttons:
        if btn.data == "Dave":
            assert btn.disabled is True

# Test approach_staff for a non-driver role (should open a confirmation dialog)
def test_approach_staff_for_non_driver():
    view = DummyView()
    page = HireStaffPage(view)
    free_agents = ["Eve"]
    # Use a non-driver role (e.g., MANAGER)
    non_driver_role = StaffRoles.COMMERCIAL_MANAGER
    page.update_free_agent_list(free_agents, non_driver_role, [])
    
    e = DummyEvent("Eve")
    page.approach_staff(e)
    
    # Verify that a dialog (dlg_modal) is created and opened
    assert hasattr(page, "dlg_modal")
    assert page.dlg_modal.open is True
    assert page.dlg_modal in view.main_app.overlay
    assert page.dlg_modal.data == "Eve"

# Test handling the confirmation dialog (Yes button)
def test_handle_close_yes():
    view = DummyView()
    page = HireStaffPage(view)
    free_agents = ["Frank"]
    non_driver_role = StaffRoles.TECHNICAL_DIRECTOR
    page.update_free_agent_list(free_agents, non_driver_role, [])
    
    # Trigger the approach to create a dialog
    e_approach = DummyEvent("Frank")
    page.approach_staff(e_approach)
    
    # Simulate clicking the "Yes" button on the dialog
    dummy_close_event = DummyEvent(None)
    dummy_close_event.control.text = "Yes"
    if hasattr(page, "dlg_modal"):
        page.dlg_modal.data = "Frank"
    page.handle_close(dummy_close_event)
    
    # Verify that the dialog has been removed from the overlay
    assert page.dlg_modal not in view.main_app.overlay
    # And that complete_hire was called
    completions = view.controller.staff_hire_controller.completions
    assert ("Frank", non_driver_role) in completions

# Test showing the accept dialog
def test_show_accept_dialog():
    view = DummyView()
    page = HireStaffPage(view)
    
    # Create a dummy accept dialog with a method to track updates
    class DummyAcceptDialog(ft.AlertDialog):
        def __init__(self, view):
            super().__init__()
            self.updated = False
        def update_text_widget(self, name, role):
            self.updated = True
            
    dummy_accept_dialog = DummyAcceptDialog(view)
    page.accept_dialog = dummy_accept_dialog
    page.show_accept_dialog("George", StaffRoles.DRIVER1)
    
    assert dummy_accept_dialog.updated is True
    assert dummy_accept_dialog.open is True
    assert dummy_accept_dialog in view.main_app.overlay

# Test showing the rejection dialog
def test_show_rejection_dialog():
    view = DummyView()
    page = HireStaffPage(view)
    
    class DummyRejectionDialog(ft.AlertDialog):
        def __init__(self):
            super().__init__()
            self.updated = False
        def update_text_widget(self, name):
            self.updated = True
            
    dummy_rejection_dialog = DummyRejectionDialog()
    page.rejection_dialog = dummy_rejection_dialog
    page.show_rejection_dialog("Hank")
    
    assert dummy_rejection_dialog.updated is True
    assert dummy_rejection_dialog.open is True
    assert dummy_rejection_dialog in view.main_app.overlay
