import random
from unittest.mock import MagicMock


from tests import create_model
from pw_model.sponsor_market.sponsor_market import SponsorMarket
from pw_model.sponsor_market import sponsor_transfers
from pw_model.pw_model_enums import SponsorTypes


def test_instantiate_market():
    model = create_model.create_model(mode="headless", auto_save=False)
    market = SponsorMarket(model)
    assert isinstance(market, SponsorMarket)
    assert market.model is model


def test_setup_dataframes_shapes():
    model = create_model.create_model(mode="headless", auto_save=False)
    market = SponsorMarket(model)
    market.setup_dataframes()
    assert market.sponsors_this_year_df.shape == (len(model.teams), 2)
    assert market.sponsors_next_year_df.shape == (len(model.teams), 2)


def test_compute_transfers_calls_determine(monkeypatch):
    model = create_model.create_model(mode="headless", auto_save=False)
    market = SponsorMarket(model)

    called = {"flag": False}

    def fake_determine(arg):
        called["flag"] = True
        assert arg is model

    monkeypatch.setattr(sponsor_transfers, "determine_sponsor_transfers", fake_determine)
    market.compute_transfers()
    assert called["flag"] is True


def test_signing_flow(monkeypatch):
    model = create_model.create_model(mode="headless", auto_save=False)
    market = SponsorMarket(model)
    market.setup_dataframes()

    monkeypatch.setattr(random, "randint", lambda *args, **kwargs: 5)

    teams = market.compile_teams_requiring_sponsor(SponsorTypes.TITLE)
    sponsors = ["Dasko", "HBRC", "PIKA"]
    for team, sponsor in zip(teams, sponsors):
        market.handle_team_signing_sponsor(team, SponsorTypes.TITLE, sponsor)

    assert market.compile_teams_requiring_sponsor(SponsorTypes.TITLE) == []

    model.season.calendar.current_week = 5
    model.inbox.new_sponsor_signed_email = MagicMock()
    market.announce_signings()

    for team, sponsor in zip(teams, sponsors):
        row = market.sponsors_next_year_announced_df.loc[
            market.sponsors_next_year_announced_df["Team"] == team
        ]
        assert row[SponsorTypes.TITLE.value].iloc[0] == sponsor


def test_update_team_sponsors(monkeypatch):
    model = create_model.create_model(mode="headless", auto_save=False)
    market = SponsorMarket(model)
    market.setup_dataframes()

    monkeypatch.setattr(random, "randint", lambda *args, **kwargs: 5)

    teams = market.compile_teams_requiring_sponsor(SponsorTypes.TITLE)
    sponsors = ["Dasko", "HBRC", "PIKA"]
    for team, sponsor in zip(teams, sponsors):
        market.handle_team_signing_sponsor(team, SponsorTypes.TITLE, sponsor)

    model.season.calendar.current_week = 5
    model.inbox.new_sponsor_signed_email = MagicMock()
    market.announce_signings()

    market.update_team_sponsors()

    for team, sponsor in zip(teams, sponsors):
        tm = model.entity_manager.get_team_model(team)
        sm = tm.finance_model.sponsorship_model
        assert sm.title_sponsor == sponsor
        assert sm.title_sponsor_model.contract.total_payment == 4_000_000
        assert sm.title_sponsor_model.contract.contract_length == 5