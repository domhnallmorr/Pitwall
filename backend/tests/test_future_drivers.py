import sqlite3
from unittest.mock import patch

from app.core.roster import load_roster
from tools.seed_roster import create_schema, seed_data


def create_seeded_db():
    conn = sqlite3.connect(":memory:")
    create_schema(conn)
    seed_data(conn)
    return conn


@patch("app.core.roster.get_connection")
def test_load_roster_includes_2000_future_drivers_with_supported_fields(mock_get_conn):
    mock_get_conn.return_value = create_seeded_db()

    _, drivers, year, _, _ = load_roster(year=2000)

    assert year == 2000
    by_name = {driver.name: driver for driver in drivers}

    tobias = by_name["Tobias Eagle"]
    adrian = by_name["Adrian Youth"]
    faustino = by_name["Faustino Asturias"]
    eugenio = by_name["Eugenio Boldini"]
    kasper = by_name["Kasper Rimmanen"]
    teodoro = by_name["Teodoro Marcello"]

    assert tobias.age == 23
    assert tobias.country == "Czech Republic"
    assert tobias.speed == 56
    assert tobias.contract_length == 0
    assert tobias.wage == 0
    assert tobias.pay_driver is False

    assert adrian.country == "Malaysia"
    assert adrian.speed == 21
    assert adrian.pay_driver is True

    assert faustino.country == "Spain"
    assert faustino.speed == 95

    assert eugenio.country == "Brazil"
    assert eugenio.speed == 59

    assert kasper.country == "Finland"
    assert kasper.speed == 89

    assert teodoro.country == "Brazil"
    assert teodoro.speed == 62
    assert teodoro.pay_driver is True

    assert all(driver.race_starts == 0 for driver in [tobias, adrian, faustino, eugenio, kasper, teodoro])
    assert all(driver.wins == 0 for driver in [tobias, adrian, faustino, eugenio, kasper, teodoro])


@patch("app.core.roster.get_connection")
def test_load_roster_includes_2001_future_drivers_with_supported_fields(mock_get_conn):
    mock_get_conn.return_value = create_seeded_db()

    _, drivers, year, _, _ = load_roster(year=2001)

    assert year == 2001
    by_name = {driver.name: driver for driver in drivers}

    toshiro = by_name["Toshiro Sakamoto"]
    alistair = by_name["Alistair Maclean"]
    mason = by_name["Mason Wyatt"]
    arthur = by_name["Arthur Dalton"]
    fabrizio = by_name["Fabrizio Moreira"]

    assert toshiro.age == 25
    assert toshiro.country == "Japan"
    assert toshiro.speed == 73

    assert alistair.age == 31
    assert alistair.country == "United Kingdom"
    assert alistair.speed == 68

    assert mason.age == 25
    assert mason.country == "Australia"
    assert mason.speed == 79

    assert arthur.age == 22
    assert arthur.country == "United Kingdom"
    assert arthur.speed == 72

    assert fabrizio.age == 20
    assert fabrizio.country == "Brazil"
    assert fabrizio.speed == 76

    assert all(driver.contract_length == 0 for driver in [toshiro, alistair, mason, arthur, fabrizio])
    assert all(driver.wage == 0 for driver in [toshiro, alistair, mason, arthur, fabrizio])
    assert all(driver.pay_driver is False for driver in [toshiro, alistair, mason, arthur, fabrizio])
    assert all(driver.race_starts == 0 for driver in [toshiro, alistair, mason, arthur, fabrizio])
    assert all(driver.wins == 0 for driver in [toshiro, alistair, mason, arthur, fabrizio])
