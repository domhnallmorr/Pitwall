import pytest
from unittest.mock import Mock
import flet as ft
from pw_view.email_page import EmailPage

def test_email_page_initialization():
    """Test the initial setup of the EmailPage."""
    mock_view = Mock()
    mock_view.page_header_style = "HeaderStyle"
    mock_view.main_app.window.height = 800
    mock_view.background_image = ft.Container()

    page = EmailPage(view=mock_view)

    # Check initial controls
    assert len(page.controls) == 1  # Initial only has header text
    assert isinstance(page.controls[0], ft.Text)
    assert page.controls[0].value == "Email"


def test_email_page_update():
    """Test the update_page method with mock data."""
    mock_view = Mock()
    mock_view.page_header_style = "HeaderStyle"
    mock_view.main_app.window.height = 800
    mock_view.background_image = ft.Container()

    mock_data = [
            Mock(subject="Subject 1", sender="Sender 1", message="Message 1"),
            Mock(subject="Subject 2", sender="Sender 2", message="Message 2"),
        ]

    page = EmailPage(view=mock_view)
    page.update_page(mock_data)

    # Check updated controls
    assert len(page.background_stack.controls) == 2  # Background image and email_row

    email_row = page.background_stack.controls[1]
    assert isinstance(email_row, ft.Row)

    email_list_container = email_row.controls[0]
    assert len(email_list_container.content.controls) == len(mock_data)


def test_show_email_content():
    """Test clicking on an email tile updates the content."""
    mock_view = Mock()
    mock_view.page_header_style = "HeaderStyle"
    mock_view.main_app.window.height = 800
    mock_view.background_image = ft.Container()

    page = EmailPage(view=mock_view)

    # Mock an email
    mock_email = Mock(subject="Subject", sender="Sender", message="Test message")
    email_tile = page.create_email_tile(mock_email)

    # Simulate click
    mock_event = Mock()
    mock_event.control.data = mock_email
    page.show_email_content(mock_event)

    # Check updated content
    assert page.email_content.value == "Test message"
