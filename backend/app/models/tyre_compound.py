from pydantic import BaseModel


class TyreCompound(BaseModel):
    supplier_name: str
    name: str
    grip: int
    wear: int
    stiffness: int
    year: int

