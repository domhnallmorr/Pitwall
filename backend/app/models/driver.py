from pydantic import BaseModel
from typing import Optional

class Driver(BaseModel):
    id: int
    name: str
    age: int
    country: str
    speed: int = 50
    consistency: int = 50
    qualifying: int = 3
    racecraft: int = 3
    race_starts: int = 0
    wins: int = 0
    podiums: int = 0
    poles: int = 0
    fastest_laps: int = 0
    championships: int = 0
    team_id: Optional[int] = None
    role: Optional[str] = None # Uses DriverRole enum string value
    points: int = 0
    wage: int = 0
    contract_length: int = 2
    pay_driver: bool = False
    active: bool = True
    retirement_year: Optional[int] = None
    retired_year: Optional[int] = None
