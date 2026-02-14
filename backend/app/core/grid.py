import pandas as pd
import json
from typing import List
from app.models.state import GameState

class GridManager:
    def get_grid_dataframe(self, state: GameState) -> pd.DataFrame:
        """
        Generates a DataFrame representing the current grid.
        Columns: Team, Country, Driver1, Driver2
        """
        data = []
        driver_lookup = {d.id: d for d in state.drivers}

        for team in state.teams:
            d1 = driver_lookup.get(team.driver1_id)
            d2 = driver_lookup.get(team.driver2_id)

            row = {
                "Team": team.name,
                "Country": team.country,
                "Driver1": d1.name if d1 else "VACANT",
                "Driver2": d2.name if d2 else "VACANT"
            }
            data.append(row)
        
        return pd.DataFrame(data)
    
    def get_grid_json(self, state: GameState) -> str:
        """Returns the grid as a JSON string for the frontend."""
        df = self.get_grid_dataframe(state)
        return df.to_json(orient="records")
