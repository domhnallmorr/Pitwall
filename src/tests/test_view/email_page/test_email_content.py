import pytest
from unittest.mock import MagicMock
import flet as ft

from pw_view.email_page.email_content import EmailContent
from pw_model.email.email_enums import EmailTypeEnums

@pytest.fixture
def mock_view():
    return MagicMock()

@pytest.fixture
def email_content(mock_view):
    return EmailContent(mock_view)

def test_email_content_initialization(email_content):
    assert email_content.subject_text.value == "Subject"
    assert email_content.from_text.value == "From:"
    assert email_content.week_text.value == "Week:"
    assert email_content.content_text.value == "Select an email to view its content"

def test_update_email_content(email_content):
    email_content.update("Test Message", "Test Subject", 14, EmailTypeEnums.CAR_DEVELOPMENT)
    
    assert email_content.subject_text.value == "Subject: Test Subject"
    assert email_content.week_text.value == "Week: 14"
    assert email_content.content_text.value == "Test Message"
    assert email_content.car_development_btn.visible is True

    # Test with a different email type
    email_content.update("Test Message", "Test Subject", 14, EmailTypeEnums.OTHER)
    assert email_content.car_development_btn.visible is False
