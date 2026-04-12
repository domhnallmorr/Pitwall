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
def test_load_roster_excludes_1999_future_drivers_from_1998(mock_get_conn):
    mock_get_conn.return_value = create_seeded_db()

    _, drivers, year, _, _ = load_roster(year=1998)

    assert year == 1998
    names = {driver.name for driver in drivers}
    assert "Luisano Burci" not in names


@patch("app.core.roster.get_connection")
def test_load_roster_includes_default_free_agents_from_1998(mock_get_conn):
    mock_get_conn.return_value = create_seeded_db()

    _, drivers, year, _, _ = load_roster(year=1998)

    assert year == 1998
    by_name = {driver.name: driver for driver in drivers}

    assert by_name["Javier Perez Mendoza"].country == "Colombia"
    assert by_name["Javier Perez Mendoza"].speed == 79
    assert by_name["Leonardo Badei"].race_starts == 34
    assert by_name["Jan van der Veen"].race_starts == 48
    assert by_name["Pablo del Rosario"].country == "Spain"
    assert by_name["Stefan Sarrien"].age == 22
    assert by_name["Jorn Maller"].country == "Germany"
    assert by_name["Jean-Claude Boulain"].country == "France"
    assert by_name["Alex Zanetto"].race_starts == 25
    assert by_name["Marco Genoa"].speed == 64
    assert by_name["Rico Zanda"].country == "Brazil"

    for name in [
        "Javier Perez Mendoza",
        "Leonardo Badei",
        "Jan van der Veen",
        "Pablo del Rosario",
        "Stefan Sarrien",
        "Jorn Maller",
        "Jean-Claude Boulain",
        "Alex Zanetto",
        "Marco Genoa",
        "Rico Zanda",
    ]:
        assert by_name[name].contract_length == 0
        assert by_name[name].wage == 0
        assert by_name[name].team_id is None


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
def test_load_roster_includes_1999_future_driver_luisano_burci(mock_get_conn):
    mock_get_conn.return_value = create_seeded_db()

    _, drivers, year, _, _ = load_roster(year=1999)

    assert year == 1999
    by_name = {driver.name: driver for driver in drivers}
    luisano = by_name["Luisano Burci"]

    assert luisano.age == 24
    assert luisano.country == "Italy"
    assert luisano.speed == 61
    assert luisano.contract_length == 0
    assert luisano.wage == 0
    assert luisano.pay_driver is False


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


@patch("app.core.roster.get_connection")
def test_load_roster_includes_2002_future_drivers_with_supported_fields(mock_get_conn):
    mock_get_conn.return_value = create_seeded_db()

    _, drivers, year, _, _ = load_roster(year=2002)

    assert year == 2002
    by_name = {driver.name: driver for driver in drivers}

    rupert = by_name["Rupert Finnegan"]
    zoltan = by_name["Zoltan Berenyi"]
    adriano = by_name["Adriano Pantanal"]
    james = by_name["James Wentworth"]
    niklas = by_name["Niklas Klint"]
    caio = by_name["Caio de Moura"]

    assert rupert.age == 27
    assert rupert.country == "Ireland"
    assert rupert.speed == 55

    assert zoltan.age == 21
    assert zoltan.country == "Hungary"
    assert zoltan.speed == 50

    assert adriano.age == 22
    assert adriano.country == "Brazil"
    assert adriano.speed == 66

    assert james.age == 24
    assert james.country == "United Kingdom"
    assert james.speed == 65

    assert niklas.age == 24
    assert niklas.country == "Denmark"
    assert niklas.speed == 50

    assert caio.age == 29
    assert caio.country == "Brazil"
    assert caio.speed == 64

    assert all(driver.contract_length == 0 for driver in [rupert, zoltan, adriano, james, niklas, caio])
    assert all(driver.wage == 0 for driver in [rupert, zoltan, adriano, james, niklas, caio])
    assert all(driver.pay_driver is False for driver in [rupert, zoltan, adriano, james, niklas, caio])
    assert all(driver.race_starts == 0 for driver in [rupert, zoltan, adriano, james, niklas, caio])
    assert all(driver.wins == 0 for driver in [rupert, zoltan, adriano, james, niklas, caio])


@patch("app.core.roster.get_connection")
def test_load_roster_includes_2003_future_drivers_with_supported_fields(mock_get_conn):
    mock_get_conn.return_value = create_seeded_db()

    _, drivers, year, _, _ = load_roster(year=2003)

    assert year == 2003
    by_name = {driver.name: driver for driver in drivers}

    caspar = by_name["Caspar Keller"]
    giovanni = by_name["Giovanni Palermo"]
    tobias = by_name["Tobias Ginter"]
    giacomo = by_name["Giacomo Bellini"]

    assert caspar.age == 20
    assert caspar.country == "Austria"
    assert caspar.speed == 59

    assert giovanni.age == 24
    assert giovanni.country == "Italy"
    assert giovanni.speed == 57

    assert tobias.age == 21
    assert tobias.country == "Germany"
    assert tobias.speed == 66

    assert giacomo.age == 22
    assert giacomo.country == "Italy"
    assert giacomo.speed == 62

    assert all(driver.contract_length == 0 for driver in [caspar, giovanni, tobias, giacomo])
    assert all(driver.wage == 0 for driver in [caspar, giovanni, tobias, giacomo])
    assert all(driver.pay_driver is False for driver in [caspar, giovanni, tobias, giacomo])
    assert all(driver.race_starts == 0 for driver in [caspar, giovanni, tobias, giacomo])
    assert all(driver.wins == 0 for driver in [caspar, giovanni, tobias, giacomo])
