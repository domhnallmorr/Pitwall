from pydantic import BaseModel
from typing import List, Dict, Any
from app.models.driver import Driver
from app.models.team import Team
from app.models.calendar import Calendar, EventType
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
    def week_display(self) -> str:
        """e.g. 'Week 1 1998'"""
        return f"Week {self.calendar.current_week} {self.year}"

    @property
    def next_event_display(self) -> str:
        """e.g. 'Next: Melbourne Grand Prix - Week 5'"""
        # Find the first event that is this week or in the future
        # Assuming events are sorted by week from the loader
        next_evt = next((e for e in self.calendar.events if e.week >= self.calendar.current_week), None)
        
        if next_evt:
            # Find circuit location
            location = next_evt.name
            for c in self.circuits:
                if c.name == next_evt.name:
                    location = c.location
                    break
            
            event_type = "Grand Prix" if next_evt.type == EventType.RACE else "Test"
            return f"Next: {location} {event_type} - Week {next_evt.week}"
        return "Next: Season Finished"

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
