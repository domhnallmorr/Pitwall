from __future__ import annotations
from typing import TYPE_CHECKING
import sqlite3

from pw_model.engine.engine_supplier_model import EngineSupplierModel

if TYPE_CHECKING:
    from pw_model.pw_base_model import Model

def load_engine_suppliers(model: Model, conn: sqlite3.Connection) -> list[EngineSupplierModel]:
    engine_suppliers = []
    
    table_name = "EngineSuppliers"
    cursor = conn.execute(f'PRAGMA table_info({table_name})')
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]

    name_idx = column_names.index("Name")
    resources_idx = column_names.index("Resources")
    power_idx = column_names.index("Power")

    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    suppliers_table = cursor.fetchall()

    for row in suppliers_table:
        name = row[name_idx]
        resources = row[resources_idx]
        power = row[power_idx]

        supplier = EngineSupplierModel(
            model,
            name=name,
            resources=resources,
            power=power
        )
        engine_suppliers.append(supplier)

    return engine_suppliers