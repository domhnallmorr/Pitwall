import pandas as pd
import json
from typing import List
from app.models.state import GameState

class GridManager:
    def _is_projected_driver_available(self, driver, current_year: int) -> bool:
        if not driver or not driver.active:
            return False
        if driver.retirement_year is not None and driver.retirement_year <= current_year:
            return False
        # Transfer placeholder rule: one year left means seat is considered open for next season.
        if getattr(driver, "contract_length", 2) == 1:
            return False
        return True

    def _is_projected_commercial_manager_available(self, manager) -> bool:
        if not manager:
            return False
        # One year remaining means seat is treated as open for next season display.
        if getattr(manager, "contract_length", 0) == 1:
            return False
        return True

    def get_grid_records(self, state: GameState, year: int | None = None) -> List[dict]:
        """
        Returns grid records for a given year.
        If snapshot exists for year, return snapshot data; otherwise return live state.
        """
        if year is not None and year in state.grid_snapshots:
            return state.grid_snapshots[year]

        if year is not None and year == state.year + 1:
            return self._build_projected_next_season_records(state)

        return self._build_live_records(state)

    def _build_live_records(self, state: GameState) -> List[dict]:
        """
        Build records representing the current live grid.
        """
        data = []
        driver_lookup = {d.id: d for d in state.drivers}
        td_lookup = {td.id: td for td in state.technical_directors}
        cm_lookup = {cm.id: cm for cm in state.commercial_managers}
        engine_country_by_name = {e.name: e.country for e in state.engine_suppliers}

        for team in state.teams:
            d1 = driver_lookup.get(team.driver1_id)
            d2 = driver_lookup.get(team.driver2_id)
            td = td_lookup.get(team.technical_director_id)
            cm = cm_lookup.get(team.commercial_manager_id)

            row = {
                "Team": team.name,
                "Country": team.country,
                "Driver1": d1.name if d1 else "VACANT",
                "Driver2": d2.name if d2 else "VACANT",
                "Driver1Country": d1.country if d1 and d1.country else "",
                "Driver2Country": d2.country if d2 and d2.country else "",
                "TechnicalDirector": td.name if td else "VACANT",
                "TechnicalDirectorCountry": td.country if td and td.country else "",
                "CommercialManager": cm.name if cm else "VACANT",
                "TitleSponsor": team.title_sponsor_name if getattr(team, "title_sponsor_name", None) else "VACANT",
                "OtherSponsorshipYearly": str(team.other_sponsorship_yearly if getattr(team, "other_sponsorship_yearly", None) is not None else 0),
                "EngineSupplier": team.engine_supplier_name if getattr(team, "engine_supplier_name", None) else "VACANT",
                "EngineSupplierCountry": engine_country_by_name.get(team.engine_supplier_name or "", ""),
                "EngineSupplierDeal": team.engine_supplier_deal if getattr(team, "engine_supplier_deal", None) else "-",
                "EngineSupplierYearlyCost": str(team.engine_supplier_yearly_cost if getattr(team, "engine_supplier_yearly_cost", None) is not None else 0),
                "TyreSupplier": team.tyre_supplier_name if getattr(team, "tyre_supplier_name", None) else "VACANT",
                "TyreSupplierDeal": team.tyre_supplier_deal if getattr(team, "tyre_supplier_deal", None) else "-",
                "TyreSupplierYearlyCost": str(team.tyre_supplier_yearly_cost if getattr(team, "tyre_supplier_yearly_cost", None) is not None else 0),
            }
            data.append(row)

        return data

    def _build_projected_next_season_records(self, state: GameState) -> List[dict]:
        """
        Build projected next-season records.
        Drivers marked to retire at end of current season are excluded from next-year seats.
        """
        data = []
        driver_lookup = {d.id: d for d in state.drivers}
        announced_by_seat = {
            (s.get("team_id"), s.get("seat")): s.get("driver_id")
            for s in state.announced_ai_signings
            if s.get("status") == "announced"
        }
        announced_cm_by_team = {
            s.get("team_id"): s.get("manager_id")
            for s in state.announced_ai_cm_signings
            if s.get("status") == "announced"
        }
        td_lookup = {td.id: td for td in state.technical_directors}
        cm_lookup = {cm.id: cm for cm in state.commercial_managers}
        engine_country_by_name = {e.name: e.country for e in state.engine_suppliers}

        for team in state.teams:
            announced_d1_id = announced_by_seat.get((team.id, "driver1_id"))
            announced_d2_id = announced_by_seat.get((team.id, "driver2_id"))
            d1 = driver_lookup.get(announced_d1_id) if announced_d1_id else driver_lookup.get(team.driver1_id)
            d2 = driver_lookup.get(announced_d2_id) if announced_d2_id else driver_lookup.get(team.driver2_id)
            if not announced_d1_id:
                d1 = d1 if self._is_projected_driver_available(d1, state.year) else None
            if not announced_d2_id:
                d2 = d2 if self._is_projected_driver_available(d2, state.year) else None
            td = td_lookup.get(team.technical_director_id)
            announced_cm_id = announced_cm_by_team.get(team.id)
            cm = cm_lookup.get(announced_cm_id) if announced_cm_id else cm_lookup.get(team.commercial_manager_id)
            if not announced_cm_id:
                cm = cm if self._is_projected_commercial_manager_available(cm) else None

            row = {
                "Team": team.name,
                "Country": team.country,
                "Driver1": d1.name if d1 else "VACANT",
                "Driver2": d2.name if d2 else "VACANT",
                "Driver1Country": d1.country if d1 and d1.country else "",
                "Driver2Country": d2.country if d2 and d2.country else "",
                "TechnicalDirector": td.name if td else "VACANT",
                "TechnicalDirectorCountry": td.country if td and td.country else "",
                "CommercialManager": cm.name if cm else "VACANT",
                "TitleSponsor": team.title_sponsor_name if getattr(team, "title_sponsor_name", None) else "VACANT",
                "OtherSponsorshipYearly": str(team.other_sponsorship_yearly if getattr(team, "other_sponsorship_yearly", None) is not None else 0),
                "EngineSupplier": team.engine_supplier_name if getattr(team, "engine_supplier_name", None) else "VACANT",
                "EngineSupplierCountry": engine_country_by_name.get(team.engine_supplier_name or "", ""),
                "EngineSupplierDeal": team.engine_supplier_deal if getattr(team, "engine_supplier_deal", None) else "-",
                "EngineSupplierYearlyCost": str(team.engine_supplier_yearly_cost if getattr(team, "engine_supplier_yearly_cost", None) is not None else 0),
                "TyreSupplier": team.tyre_supplier_name if getattr(team, "tyre_supplier_name", None) else "VACANT",
                "TyreSupplierDeal": team.tyre_supplier_deal if getattr(team, "tyre_supplier_deal", None) else "-",
                "TyreSupplierYearlyCost": str(team.tyre_supplier_yearly_cost if getattr(team, "tyre_supplier_yearly_cost", None) is not None else 0),
            }
            data.append(row)

        return data

    def capture_season_snapshot(self, state: GameState, year: int | None = None):
        """Persist a season grid snapshot to state for historical/future display."""
        snapshot_year = year if year is not None else state.year
        state.grid_snapshots[snapshot_year] = self._build_live_records(state)

    def get_grid_dataframe(self, state: GameState, year: int | None = None) -> pd.DataFrame:
        """
        Generates a DataFrame representing the grid for a given year.
        Columns: Team, Country, Driver1, Driver2, TechnicalDirector
        """
        return pd.DataFrame(self.get_grid_records(state, year=year))

    def get_grid_json(self, state: GameState, year: int | None = None) -> str:
        """Returns the grid as a JSON string for the frontend."""
        df = self.get_grid_dataframe(state, year=year)
        return df.to_json(orient="records")
