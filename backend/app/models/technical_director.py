from pydantic import BaseModel
from typing import Optional


class TechnicalDirector(BaseModel):
    id: int
    name: str
    country: Optional[str] = None
    age: int
    skill: int
    contract_length: int = 0
    salary: int = 0
    team_id: Optional[int] = None
    active: bool = True
    retirement_year: Optional[int] = None
    retired_year: Optional[int] = None
