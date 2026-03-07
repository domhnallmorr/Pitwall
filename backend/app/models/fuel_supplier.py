from pydantic import BaseModel


class FuelSupplier(BaseModel):
    id: int
    name: str
    country: str
    resources: int = 0
    r_and_d: int = 0
    start_year: int = 0
