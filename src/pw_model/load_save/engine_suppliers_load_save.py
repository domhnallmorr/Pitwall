from __future__ import annotations
from typing import TYPE_CHECKING
import sqlite3

from pw_model.engine.engine_supplier_model import EngineSupplierModel

if TYPE_CHECKING:
    from pw_model.pw_base_model import Model

def save_engine_suppliers(model: Model, save_file: sqlite3.Connection) -> None:
    cursor = save_file.cursor()
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS "EngineSuppliers" (
            "Name" TEXT,
            "Resources" INTEGER,
            "Power" INTEGER
            )'''
        )
    cursor.execute("DELETE FROM EngineSuppliers")  # Clear existing data

    for supplier in model.engine_suppliers:
        cursor.execute('''
            INSERT INTO EngineSuppliers (Name, Resources, Power)
            VALUES (?, ?, ?)
        ''', (
            supplier.name,
            supplier.resources,
            supplier.power
        ))

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