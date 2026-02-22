from pydantic import BaseModel
from typing import Optional

class Team(BaseModel):
    id: int
    name: str
    country: str
    car_speed: int = 50
    workforce: int = 0
    title_sponsor_name: str | None = None
    title_sponsor_yearly: int = 0
    engine_supplier_name: str | None = None
    engine_supplier_deal: str | None = None
    engine_supplier_yearly_cost: int = 0
    tyre_supplier_name: str | None = None
    tyre_supplier_deal: str | None = None
    tyre_supplier_yearly_cost: int = 0
    technical_director_id: Optional[int] = None
    commercial_manager_id: Optional[int] = None
    driver1_id: Optional[int] = None
    driver2_id: Optional[int] = None
    points: int = 0
    balance: int = 0
    facilities: int = 0
