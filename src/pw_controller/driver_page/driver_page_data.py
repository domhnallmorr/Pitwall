from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from pw_model.pw_base_model import Model
    from pw_model.driver.driver_model import DriverModel


@dataclass(frozen=True)
class DriverPageData:
    name: str
    age: int
    country: str
    salary: int
    contract_length: int
    retiring: bool
    starts: int
    championships: int
    wins: int
    speed: int
    consistency: int
    qualifying: int
    race_results_df: pd.DataFrame
    qualy_results_df: pd.DataFrame
    race_countries: list[str]


def get_driver_page_data(model: Model, driver_name: str) -> DriverPageData:
    driver_model: DriverModel = model.entity_manager.get_driver_model(driver_name)
    return DriverPageData(
        name=driver_model.name,
        age=driver_model.age,
        country=driver_model.country,
        salary=driver_model.contract.salary,
        contract_length=driver_model.contract.contract_length,
        retiring=driver_model.retiring,
        starts=driver_model.career_stats.starts,
        championships=driver_model.career_stats.championships,
        wins=driver_model.career_stats.wins,
        speed=driver_model.speed,
        consistency=driver_model.consistency,
        qualifying=driver_model.qualifying,
        race_results_df=driver_model.season_stats.race_results_df,
        qualy_results_df=driver_model.season_stats.qualy_results_df,
        race_countries=model.season.calendar.countries,
    )