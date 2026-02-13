from pydantic import BaseModel
from typing import List, Dict, Any
from app.models.driver import Driver
from app.models.team import Team
from app.models.calendar import Calendar
from app.models.circuit import Circuit
import pandas as pd
import json

class GameState(BaseModel):
    year: int
    teams: List[Team]
    drivers: List[Driver]
    calendar: Calendar
    circuits: List[Circuit]
    player_team_id: int | None = None
    
    @property
    def current_date(self) -> str:
        """Dynamic date string based on Calendar state."""
        evt = self.calendar.current_event
        if evt:
            return f"{evt.name} - Week {self.calendar.current_week}"
        return f"Week {self.calendar.current_week}"

    model_config = {
        "arbitrary_types_allowed": True 
    }

    def get_grid_dataframe(self) -> pd.DataFrame:
        """
        Generates a DataFrame representing the current grid.
        Columns: Team, Country, Driver1, Driver2
        """
        data = []
        driver_lookup = {d.id: d for d in self.drivers}

        for team in self.teams:
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
    
    def get_grid_json(self) -> str:
        """Returns the grid as a JSON string for the frontend."""
        df = self.get_grid_dataframe()
        return df.to_json(orient="records")
