from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum
from app.models.circuit import Circuit

class EventType(str, Enum):
    RACE = "RACE"
    TEST = "TEST"

class Event(BaseModel):
    name: str
    week: int
    type: EventType

class Calendar(BaseModel):
    events: List[Event]
    current_week: int = 1 # Start at week 1
    
    @property
    def current_event(self) -> Optional[Event]:
        """Returns the event for the current week, if any."""
        for event in self.events:
            if event.week == self.current_week:
                return event
        return None

    def advance_week(self):
        """Advances the calendar by one week."""
        self.current_week += 1

    @property
    def last_event_week(self) -> int:
        """Returns the week number of the last event in the season."""
        if not self.events:
            return 0
        return max(e.week for e in self.events)

    @property
    def season_over(self) -> bool:
        """True if the current week is past the last event."""
        return self.current_week > self.last_event_week

    def get_schedule_data(self, circuits: List[Circuit]) -> List[Dict[str, Any]]:
        """
        Returns a list of dictionaries representing the schedule for the UI.
        Format: {round, week, track, country, winner}
        """
        schedule = []
        race_counter = 0
        
        # Create a lookup for circuits by name for O(1) access
        circuit_map = {c.name: c for c in circuits}

        for event in self.events:
            round_display = "-"
            if event.type == EventType.RACE:
                race_counter += 1
                round_display = str(race_counter)
            
            # Lookup country
            country = "Unknown"
            if event.name in circuit_map:
                country = circuit_map[event.name].country
            
            type_display = "Grand Prix" if event.type == EventType.RACE else "Test"

            schedule.append({
                "round": round_display,
                "week": event.week,
                "type": type_display,
                "track": event.name,
                "country": country,
                "winner": "" # Placeholder
            })
            
        return schedule

    def get_next_event_display(self, circuits: List[Circuit]) -> str:
        """
        Returns a string describing the next upcoming event.
        e.g. 'Next: Melbourne Grand Prix - Week 5'
        """
        # Find the first event that is this week or in the future
        next_evt = next((e for e in self.events if e.week >= self.current_week), None)
        
        if next_evt:
            # Find circuit location
            location = next_evt.name
            for c in circuits:
                if c.name == next_evt.name:
                    location = c.location
                    break
            
            event_type = "Grand Prix" if next_evt.type == EventType.RACE else "Test"
            return f"Next: {location} {event_type} - Week {next_evt.week}"
        
        return "Next: Season Finished"
