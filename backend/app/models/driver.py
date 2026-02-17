from pydantic import BaseModel
from typing import Optional

class Driver(BaseModel):
    id: int
    name: str
    age: int
    country: str
    speed: int = 50
    race_starts: int = 0
    wins: int = 0
    team_id: Optional[int] = None
    role: Optional[str] = None # Uses DriverRole enum string value
    points: int = 0
    wage: int = 0
    pay_driver: bool = False
    active: bool = True
    retirement_year: Optional[int] = None
    retired_year: Optional[int] = None
