from __future__ import annotations
from typing import TYPE_CHECKING
import sqlite3

from pw_model.finance.transport_costs import TransportCostsModel

if TYPE_CHECKING:
    from pw_model.pw_base_model import Model


def save_transport_costs_model(transport_costs: TransportCostsModel, save_file: sqlite3.Connection) -> None:
	cursor = save_file.cursor()
	cursor.execute('''
			CREATE TABLE IF NOT EXISTS "transport_costs" (
            "EstimatedCosts" INTEGER,
			"TotalCosts" INTEGER,
            "CostsByRace" TEXT,
            "CostsByTest" TEXT
            )'''
        )
	cursor.execute("DELETE FROM transport_costs")  # Clear existing data

	cursor.execute('''
            INSERT INTO transport_costs (EstimatedCosts, TotalCosts, CostsByRace, CostsByTest)
            VALUES (?, ?, ?, ?)
        ''', (
            transport_costs.estimated_season_costs,
            transport_costs.total_costs,
            ','.join(map(str, transport_costs.costs_by_race)),
            ','.join(map(str, transport_costs.costs_by_test)),
        ))

def load_transport_costs(conn: sqlite3.Connection, transport_costs_model: TransportCostsModel) -> None:
    """
    Load transport costs data from the SQLite database into the TransportCostsModel instance.

    Args:
        conn (sqlite3.Connection): SQLite database connection object.
        transport_costs_model (TransportCostsModel): Instance of the TransportCostsModel to populate.
    """
    cursor = conn.cursor()

    # Check if the table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transport_costs'")
    if not cursor.fetchone():
        raise ValueError("The 'transport_costs' table does not exist in the database.")

    # Load data from the table
    cursor.execute("SELECT EstimatedCosts, TotalCosts, CostsByRace, CostsByTest FROM transport_costs")
    result = cursor.fetchone()

    if result:
        estimated_season_costs, total_costs, costs_by_race, costs_by_test = result

        # Populate the TransportCostsModel instance
        transport_costs_model.estimated_season_costs = estimated_season_costs
        transport_costs_model.total_costs = total_costs
        transport_costs_model.costs_by_race = [int(cost) for cost in costs_by_race.split(",") if cost.strip()]
        transport_costs_model.costs_by_test = [int(cost) for cost in costs_by_test.split(",") if cost.strip()]
    else:
        # Handle case where no data exists in the table
        raise ValueError("The 'transport_costs' table is empty")