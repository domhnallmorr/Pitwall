from __future__ import annotations
from typing import TYPE_CHECKING
import sqlite3

from pw_model.pw_model_enums import StaffRoles

if TYPE_CHECKING:
    from pw_model.pw_base_model import Model
   

def save_team_principals(model: Model, save_file: sqlite3.Connection) -> None:
    cursor = save_file.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS "TeamPrincipals" (
        "Year"  TEXT,
        "Name"  TEXT,
        "Age"   INTEGER,
        "Skill" INTEGER,
        "Salary" INTEGER,
        "ContractLength" INTEGER,
        "RetiringAge" INTEGER,
        "Retiring" INTEGER,
        "Retired" INTEGER
        )'''
    )
    
    cursor.execute("DELETE FROM TeamPrincipals")  # Clear existing data

    # Save current team principals
    for team_principal_model in model.team_principals:
            cursor.execute('''
                INSERT INTO TeamPrincipals (
                    Year, Name, Age, Skill, Salary, ContractLength, 
                    RetiringAge, Retiring, Retired
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                "default",
                team_principal_model.name,
                team_principal_model.age,
                team_principal_model.skill,
                team_principal_model.contract.salary,
                team_principal_model.contract.contract_length,
                team_principal_model.retiring_age,
                team_principal_model.retiring,
                team_principal_model.retired
            ))

    # Save future team principals
    for future_manager in model.future_managers:
        if future_manager[1].role == StaffRoles.TEAM_PRINCIPAL:
            year = future_manager[0]
            tp = future_manager[1]
            cursor.execute('''
                INSERT INTO TeamPrincipals (
                    Year, Name, Age, Skill, Salary, ContractLength, 
                    RetiringAge, Retiring, Retired
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                year,
                tp.name,
                tp.age,
                tp.skill,
                tp.contract.salary,
                tp.contract.contract_length,
                tp.retiring_age,
                tp.retiring,
                tp.retired
            ))


