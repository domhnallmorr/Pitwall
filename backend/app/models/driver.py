from pydantic import BaseModel
from typing import Optional

class Driver(BaseModel):
    id: int
    name: str
    age: int
    country: str
    team_id: Optional[int] = None
    role: Optional[str] = None # Uses DriverRole enum string value
    points: int = 0
    wage: int = 0
    pay_driver: bool = False
