from pydantic import BaseModel
from typing import List, Dict, Any
from app.models.driver import Driver
from app.models.team import Team
from app.models.calendar import Calendar, EventType
from app.models.circuit import Circuit
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
        """Delegates to Calendar model"""
        return self.calendar.get_next_event_display(self.circuits)

    model_config = {
        "arbitrary_types_allowed": True 
    }
