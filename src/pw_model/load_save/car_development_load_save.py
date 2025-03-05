from __future__ import annotations
from typing import TYPE_CHECKING
import sqlite3

from pw_model.car_development.car_development_model import CarDevelopmentEnums, CarDevelopmentStatusEnums

if TYPE_CHECKING:
    from pw_model.pw_base_model import Model

def save_car_development(model: Model, save_file: sqlite3.Connection) -> None:
        
    cursor = save_file.cursor()
    # Save current development status for player team
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS "car_development" (
        "Team"                  TEXT,
        "CurrentStatus"         TEXT,
        "TimeLeft"             INTEGER,
        "DevelopmentType"      TEXT
        )'''
    )
    
    cursor.execute("DELETE FROM car_development")  # Clear existing data

    car_dev = model.player_team_model.car_development_model
    
    cursor.execute('''
        INSERT INTO car_development (Team, CurrentStatus, TimeLeft, DevelopmentType)
        VALUES (?, ?, ?, ?)
    ''', (
        model.player_team,
        car_dev.current_status.value,
        car_dev.time_left,
        car_dev.current_development_type.value
    ))

    # Save planned updates for all teams
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS "car_development_planned_updates" (
        "Team"              TEXT,
        "Week"             INTEGER,
        "DevelopmentType"  TEXT
        )'''
    )
    
    cursor.execute("DELETE FROM car_development_planned_updates")  # Clear existing data
    
    # Save planned updates for all teams
    for team in model.teams:
        car_dev = team.car_development_model
        for update in car_dev.planned_updates:
            week = update[0]
            dev_type = update[1]            
            cursor.execute('''
                INSERT INTO car_development_planned_updates (Team, Week, DevelopmentType)
                VALUES (?, ?, ?)
            ''', (
                team.name,
                week,
                dev_type.value
            ))

def load_car_development(conn: sqlite3.Connection, model: Model) -> None:
    if not model.player_team_model:
        return
        
    cursor = conn.cursor()
    # Load current development status for player team
    cursor.execute("SELECT * FROM car_development WHERE Team = ?", (model.player_team,))
    row = cursor.fetchone()
    
    if row:
        car_dev = model.player_team_model.car_development_model
        car_dev.current_status = CarDevelopmentStatusEnums(row[1])
        car_dev.time_left = row[2]
        car_dev.current_development_type = CarDevelopmentEnums(row[3])

    # Load planned updates for all teams
    cursor.execute("SELECT Team, Week, DevelopmentType FROM car_development_planned_updates")
    rows = cursor.fetchall()
    
    # Group updates by team
    for team in model.teams:
        team_updates = [(row[1], CarDevelopmentEnums(row[2])) 
                       for row in rows if row[0] == team.name]
        team.car_development_model.planned_updates = team_updates
