from pydantic import BaseModel


class TyreSupplier(BaseModel):
    id: int
    name: str
    country: str
    wear: int = 0
    grip: int = 0
    resources: int = 0
    innovation: int = 0
    reliability: int = 0
    start_year: int = 0
