import sys
import types
import flet as ft
import pytest

# --- Map your flat files onto the dotted paths that hire_staff_page expects ---
from pw_model import pw_model_enums as _enums
from pw_model.driver_negotiation import driver_interest as _interest
from pw_view.custom_widgets import custom_container as _custom_container
from pw_view.staff_page import staff_dialogs as _staff_dialogs

# pw_model.pw_model_enums
sys.modules["pw_model"] = types.ModuleType("pw_model")
sys.modules["pw_model.pw_model_enums"] = _enums

# pw_model.driver_negotiation.driver_interest
sys.modules.setdefault("pw_model.driver_negotiation", types.ModuleType("pw_model.driver_negotiation"))
sys.modules["pw_model.driver_negotiation.driver_interest"] = _interest

# pw_view.custom_widgets.custom_container
sys.modules.setdefault("pw_view", types.ModuleType("pw_view"))
sys.modules.setdefault("pw_view.custom_widgets", types.ModuleType("pw_view.custom_widgets"))
sys.modules["pw_view.custom_widgets.custom_container"] = _custom_container

# pw_view.staff_page.staff_dialogs
sys.modules.setdefault("pw_view.staff_page", types.ModuleType("pw_view.staff_page"))
sys.modules["pw_view.staff_page.staff_dialogs"] = _staff_dialogs

# --- Now import the page under test (your real file) ---
from pw_view.staff_page import hire_staff_page as page_mod

StaffRoles = _enums.StaffRoles

# --- Minimal fakes for View / Controller / MainApp so the page can run ------
class FakeMainApp:
    def __init__(self):
        class _Window: pass
        self.window = _Window()
        self.window.height = 800
        self.overlay = []
        self._updates = 0
    def update(self): self._updates += 1
    def close(self, dlg):
        if dlg in self.overlay:
            self.overlay.remove(dlg)

class FakeMainWindow:
    def __init__(self): self.last_page = None
    def change_page(self, p): self.last_page = p

class FakePageHeaderStyle: ...

class FakeController:
    """
    Acts as controller.staff_hire_controller for the page.
    """
    def __init__(self):
        self.staff_hire_controller = self
        self._details = {}
        self.open_driver_offer_dialog_calls = []
        self.view = None  # set by FakeView
    def get_staff_details(self, name, role):
        return self._details[name]
    def open_driver_offer_dialog(self, driver_name, role):
        self.open_driver_offer_dialog_calls.append((driver_name, role))

class FakeView:
    def __init__(self, controller):
        self.controller = controller
        controller.view = self
        self.main_app = FakeMainApp()
        self.main_window = FakeMainWindow()
        self.page_header_style = FakePageHeaderStyle()
        self.background_image = ft.Container()
        self.vscroll_buffer = 160
        self.driver_images_path = "path/to/driver/images"

        self.dark_grey = "#23232A"

# ------------------------------ Tests ---------------------------------------

@pytest.fixture
def fx():
    controller = FakeController()
    view = FakeView(controller)
    page = page_mod.HireStaffPage(view)
    return controller, view, page

def test_offer_button_disables_when_driver_previously_approached(fx):
    controller, view, hp = fx

    # Seed details; Alice previously approached, Bob not.
    controller._details = {
        "Alice": {"name": "Alice", "age": 21, "rejected_player_offer": True},
        "Bob":   {"name": "Bob",   "age": 25, "rejected_player_offer": False},
    }

    # Populate list for driver hiring
    hp.update_free_agent_list(["Alice", "Bob"], StaffRoles.DRIVER1, pay_drivers=[], ratings=[50, 50])

    # After auto-select (first in list), Offer should be disabled for Alice
    assert hp.offer_btn.data == "Alice"
    assert hp.offer_btn.disabled is True

    # Selecting Bob should enable Offer
    hp.update_staff(None, name="Bob")
    assert hp.offer_btn.data == "Bob"
    assert hp.offer_btn.disabled is False

def test_clicking_offer_calls_controller_when_enabled(fx):
    controller, view, hp = fx

    controller._details = {
        "Bob": {"name": "Bob", "age": 25, "rejected_player_offer": False},
    }
    hp.update_free_agent_list(["Bob"], StaffRoles.DRIVER2, pay_drivers=[], ratings=[50])

    # Simulate clicking "Offer"
    class E:
        class C: pass
        def __init__(self, data):
            self.control = self.C()
            self.control.data = data

    hp.approach_staff(E("Bob"))
    assert controller.open_driver_offer_dialog_calls == [("Bob", StaffRoles.DRIVER2)]
