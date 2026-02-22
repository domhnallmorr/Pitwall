from pydantic import BaseModel, Field
from typing import List, Dict, Any
from app.models.driver import Driver
from app.models.team import Team
from app.models.technical_director import TechnicalDirector
from app.models.commercial_manager import CommercialManager
from app.models.title_sponsor import TitleSponsor
from app.models.engine_supplier import EngineSupplier
from app.models.tyre_supplier import TyreSupplier
from app.models.calendar import Calendar
from app.models.circuit import Circuit
from app.models.email import Email, EmailCategory
from app.models.finance import Finance


class QueuedEmail(BaseModel):
    sender: str
    subject: str
    body: str
    week: int
    year: int
    category: EmailCategory = EmailCategory.GENERAL

class GameState(BaseModel):
    year: int
    teams: List[Team]
    drivers: List[Driver]
    technical_directors: List[TechnicalDirector] = Field(default_factory=list)
    commercial_managers: List[CommercialManager] = Field(default_factory=list)
    title_sponsors: List[TitleSponsor] = Field(default_factory=list)
    engine_suppliers: List[EngineSupplier] = Field(default_factory=list)
    tyre_suppliers: List[TyreSupplier] = Field(default_factory=list)
    calendar: Calendar
    circuits: List[Circuit]
    player_team_id: int | None = None
    events_processed: List[str] = Field(default_factory=list) # Track events handled this week/season
    emails: List[Email] = Field(default_factory=list)
    next_email_id: int = 1
    finance: Finance = Field(default_factory=Finance)
    queued_emails: List[QueuedEmail] = Field(default_factory=list)
    grid_snapshots: Dict[int, List[Dict[str, str]]] = Field(default_factory=dict)
    driver_season_results: Dict[int, Dict[int, List[Dict[str, Any]]]] = Field(default_factory=dict)
    latest_race_incidents: List[Dict[str, Any]] = Field(default_factory=list)

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

    def queue_email(self, sender: str, subject: str, body: str, week: int, year: int,
                    category: EmailCategory = EmailCategory.GENERAL):
        """Queue an email for delivery on a specific week/year."""
        self.queued_emails.append(QueuedEmail(
            sender=sender,
            subject=subject,
            body=body,
            week=week,
            year=year,
            category=category
        ))

    def publish_queued_emails(self, week: int | None = None, year: int | None = None) -> int:
        """Publish queued emails due for the supplied or current game week/year."""
        target_week = week if week is not None else self.calendar.current_week
        target_year = year if year is not None else self.year
        remaining: List[QueuedEmail] = []
        published = 0

        for queued in self.queued_emails:
            if queued.week == target_week and queued.year == target_year:
                self.add_email(
                    sender=queued.sender,
                    subject=queued.subject,
                    body=queued.body,
                    category=queued.category
                )
                published += 1
            else:
                remaining.append(queued)

        self.queued_emails = remaining
        return published
    
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
