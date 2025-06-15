from __future__ import annotations
from typing import TYPE_CHECKING

from pw_controller.driver_page.driver_page_data import get_driver_page_data
from pw_view.view_enums import ViewPageEnums

if TYPE_CHECKING:
    from pw_controller.pw_controller import Controller
    from pw_model.pw_base_model import Model


class DriverPageController:
    def __init__(self, controller: Controller):
        self.controller = controller

    @property
    def model(self) -> Model:
        return self.controller.model

    def go_to_driver_page(self, driver_name: str) -> None:
        data = get_driver_page_data(self.model, driver_name)
        self.controller.view.driver_page.update_page(data)
        self.controller.view.main_window.change_page(ViewPageEnums.DRIVER)