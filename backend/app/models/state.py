from pydantic import BaseModel
from typing import List, Dict, Any
from app.models.driver import Driver
from app.models.team import Team
from app.models.calendar import Calendar, EventType
from app.models.circuit import Circuit
from app.models.email import Email, EmailCategory
from app.models.finance import Finance
import json

class GameState(BaseModel):
    year: int
    teams: List[Team]
    drivers: List[Driver]
    calendar: Calendar
    circuits: List[Circuit]
    player_team_id: int | None = None
    events_processed: List[str] = [] # Track events handled this week/season
    emails: List[Email] = []
    next_email_id: int = 1
    finance: Finance = Finance()

    def add_email(self, sender: str, subject: str, body: str, 
                  category: EmailCategory = EmailCategory.GENERAL) -> Email:
        """Creates and adds a new email to the inbox."""
        email = Email(
            id=self.next_email_id,
            sender=sender,
            subject=subject,
            body=body,
            week=self.calendar.current_week,
            year=self.year,
            category=category
        )
        self.emails.append(email)
        self.next_email_id += 1
        return email
    
    @property
    def player_team(self):
        """Returns the player's team object."""
        for t in self.teams:
            if t.id == self.player_team_id:
                return t
        return None

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
