import pytest

from tests import create_model


def test_drivers_by_rating_sorted_and_complete():
    model = create_model.create_model()
    drivers = model.season.drivers_by_rating

    ratings = [rating for _, rating in drivers]
    assert ratings == sorted(ratings, reverse=True)

    expected_names = {
        team.driver1 for team in model.teams
    } | {
        team.driver2 for team in model.teams
    }
    returned_names = {name for name, _ in drivers}
    assert returned_names == expected_names


def test_teams_by_rating_sorted_and_complete():
    model = create_model.create_model()
    teams = model.season.teams_by_rating

    ratings = [rating for _, rating in teams]
    assert ratings == sorted(ratings, reverse=True)

    expected_names = {team.name for team in model.teams}
    returned_names = {name for name, _ in teams}
    assert returned_names == expected_names


def test_technical_directors_by_rating_sorted_and_complete():
    model = create_model.create_model()
    tds = model.season.technical_directors_by_rating

    ratings = [rating for _, rating in tds]
    assert ratings == sorted(ratings, reverse=True)

    expected_names = {team.technical_director for team in model.teams}
    returned_names = {name for name, _ in tds}
    assert returned_names == expected_names