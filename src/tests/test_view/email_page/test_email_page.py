import pytest
from unittest.mock import MagicMock
from collections import deque
import flet as ft

from pw_view.email_page.email_page import EmailPage
from pw_view.email_page.email_tile import EmailTile
from pw_model.email.email_model import Email, EmailStatusEnums

@pytest.fixture
def mock_view():
    view = MagicMock()
    view.page_header_style = "Test Style"
    view.background_image = ft.Container()
    view.controller = MagicMock()
    view.main_app = MagicMock()
    return view

@pytest.fixture
def sample_emails():
    return deque([
        Email("Subject 1", "Message 1", 1, EmailStatusEnums.UNREAD, "Sender 1"),
        Email("Subject 2", "Message 2", 2, EmailStatusEnums.READ, "Sender 2"),
    ])

@pytest.fixture
def email_page(mock_view):
    return EmailPage(mock_view)

def test_email_page_initialization(email_page):
    assert email_page.email_list is not None
    assert email_page.email_content is not None
    assert isinstance(email_page.email_list, ft.ListView)
    assert email_page.selected_email is None

def test_update_page(email_page, sample_emails):
    email_tiles = [EmailTile(email_page.view, email, email_page.show_email_content) for email in sample_emails]
    email_page.update_page(sample_emails)
    
    assert len(email_page.email_list.controls) == len(sample_emails)
    assert email_page.selected_email is not None

def test_show_email_content(email_page, sample_emails):
    email_tile = EmailTile(email_page.view, sample_emails[0], email_page.show_email_content)
    email_page.show_email_content(email_tile)
    
    assert email_page.selected_email == email_tile
    assert email_page.email_content.subject_text.value == f"Subject: {sample_emails[0].subject}"
    assert email_page.email_content.content_text.value == sample_emails[0].message
