from pydantic import BaseModel


class EngineSupplier(BaseModel):
    id: int
    name: str
    country: str
    resources: int = 0
    power: int = 0
    start_year: int = 0

