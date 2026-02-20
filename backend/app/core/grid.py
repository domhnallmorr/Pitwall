import pandas as pd
import json
from typing import List
from app.models.state import GameState

class GridManager:
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
                "TechnicalDirector": td.name if td else "VACANT",
                "TechnicalDirectorCountry": td.country if td and td.country else "",
                "CommercialManager": cm.name if cm else "VACANT",
                "TitleSponsor": team.title_sponsor_name if getattr(team, "title_sponsor_name", None) else "VACANT",
            }
            data.append(row)

        return data

    def _build_projected_next_season_records(self, state: GameState) -> List[dict]:
        """
        Build projected next-season records.
        Drivers marked to retire at end of current season are excluded from next-year seats.
        """
        data = []
        projected_driver_lookup = {
            d.id: d for d in state.drivers
            if d.active and (d.retirement_year is None or d.retirement_year > state.year)
        }
        td_lookup = {td.id: td for td in state.technical_directors}
        cm_lookup = {cm.id: cm for cm in state.commercial_managers}

        for team in state.teams:
            d1 = projected_driver_lookup.get(team.driver1_id)
            d2 = projected_driver_lookup.get(team.driver2_id)
            td = td_lookup.get(team.technical_director_id)
            cm = cm_lookup.get(team.commercial_manager_id)

            row = {
                "Team": team.name,
                "Country": team.country,
                "Driver1": d1.name if d1 else "VACANT",
                "Driver2": d2.name if d2 else "VACANT",
                "TechnicalDirector": td.name if td else "VACANT",
                "TechnicalDirectorCountry": td.country if td and td.country else "",
                "CommercialManager": cm.name if cm else "VACANT",
                "TitleSponsor": team.title_sponsor_name if getattr(team, "title_sponsor_name", None) else "VACANT",
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
