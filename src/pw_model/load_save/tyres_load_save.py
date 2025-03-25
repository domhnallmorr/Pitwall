from __future__ import annotations
from typing import TYPE_CHECKING
import sqlite3

from pw_model.tyre.tyre_supplier_model import TyreSupplierModel

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model

def save_tyre_suppliers(model: Model, save_file: sqlite3.Connection) -> None:
	cursor = save_file.cursor()
	cursor.execute('''
			CREATE TABLE IF NOT EXISTS "TyreSuppliers" (
            "Name" TEXT,
			"Wear" INTEGER,
            "Grip" INTEGER
            )'''
        )
	cursor.execute("DELETE FROM TyreSuppliers")  # Clear existing data

	for supplier in model.tyre_suppliers:
		cursor.execute('''
			INSERT INTO TyreSuppliers (Name, Wear, Grip)
			VALUES (?, ?, ?)
		''', (
			supplier.name,
			supplier.compound.wear,
			supplier.compound.grip
		))



def load_tyre_suppliers(model: Model, conn: sqlite3.Connection) -> list[TyreSupplierModel]:
	tyre_suppliers = []
	
	table_name = "TyreSuppliers"
	cursor = conn.execute(f'PRAGMA table_info({table_name})')
	columns = cursor.fetchall()
	column_names = [column[1] for column in columns]

	name_idx = column_names.index("Name")
	wear_idx = column_names.index("Wear")
	grip_idx = column_names.index("Grip")

	cursor = conn.cursor()
	cursor.execute(f"SELECT * FROM {table_name}")
	suppliers_table = cursor.fetchall()

	for row in suppliers_table:
		name = row[name_idx]
		wear = row[wear_idx]
		grip = row[grip_idx]

		supplier = TyreSupplierModel(name, wear, grip)
		tyre_suppliers.append(supplier)

	return tyre_suppliers