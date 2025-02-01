import pytest
from unittest.mock import MagicMock
import flet as ft

from pw_view.email_page.email_tile import EmailTile
from pw_model.email.email_model import Email, EmailStatusEnums

@pytest.fixture
def mock_view():
    view = MagicMock()
    view.dark_grey = "#333333"
    view.primary_selected_color = "#FFCC00"
    return view

@pytest.fixture
def sample_email():
    return Email("Test Subject", "Test Message", 1, EmailStatusEnums.UNREAD, "Test Sender")

@pytest.fixture
def email_tile(mock_view, sample_email):
    return EmailTile(mock_view, sample_email, MagicMock())

def test_email_tile_initialization(email_tile, sample_email):
    assert email_tile.email == sample_email
    assert email_tile.title_text.value == f"RE: {sample_email.subject}"
    assert email_tile.subtitle_text.value == f"From: {sample_email.sender}"
    assert email_tile.bgcolor == ft.Colors.PRIMARY

def test_tile_selected(email_tile):
    email_tile.tile_selected()
    assert email_tile.bgcolor == email_tile.view.primary_selected_color
    assert email_tile.title_text.color == email_tile.view.dark_grey
    assert email_tile.subtitle_text.color == email_tile.view.dark_grey

def test_tile_unselected(email_tile):
    email_tile.tile_unselected()
    assert email_tile.bgcolor == ft.Colors.GREY
    assert email_tile.title_text.color == email_tile.view.dark_grey
    assert email_tile.subtitle_text.color == email_tile.view.dark_grey
