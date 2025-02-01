import pytest
from unittest.mock import MagicMock
import flet as ft

from pw_view.email_page.email_list import EmailList
from pw_view.email_page.email_tile import EmailTile
from pw_model.email.email_model import Email, EmailStatusEnums

@pytest.fixture
def mock_view():
    return MagicMock()

@pytest.fixture
def mock_email_page():
    return MagicMock()

@pytest.fixture
def sample_emails():
    return [
        Email("Subject 1", "Message 1", 1, EmailStatusEnums.UNREAD, "Sender 1"),
        Email("Subject 2", "Message 2", 2, EmailStatusEnums.READ, "Sender 2"),
    ]

@pytest.fixture
def email_list(mock_view, mock_email_page):
    return EmailList(mock_view, mock_email_page)

def test_email_list_initialization(email_list):
    assert isinstance(email_list, ft.ListView)
    assert email_list.controls == []

def test_update_content(email_list, sample_emails):
    email_tiles = [MagicMock(email=email) for email in sample_emails]
    email_list.email_tiles = email_tiles  # Ensure email_tiles is set
    email_list.update_content(sample_emails, selected_id=1)
    
    assert len(email_list.controls) == len(sample_emails)

def test_create_email_tiles(email_list, sample_emails):
    email_list.create_email_tile = MagicMock()
    email_list.create_email_tiles(sample_emails)
    assert len(email_list.create_email_tile.call_args_list) == len(sample_emails)
