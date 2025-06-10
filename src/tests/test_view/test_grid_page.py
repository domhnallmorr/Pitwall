import pytest
import pandas as pd
import flet as ft

from pw_view.grid_page import GridPage               # :contentReference[oaicite:1]{index=1}
from pw_model.pw_model_enums import SponsorTypes     # :contentReference[oaicite:2]{index=2}

@pytest.fixture
def dummy_view():
    """A minimal stand-in for the real View, supplying only what GridPage and CustomDataTable need."""
    class DummyMainApp:
        def __init__(self):
            self.updated = False
        def update(self):
            self.updated = True

    view = type("V", (), {})()
    view.background_image    = ft.Text("BG")                    # used in GridPage.__init__
    view.page_header_style  = ft.TextThemeStyle.DISPLAY_SMALL  # used for header Text
    view.main_app           = DummyMainApp()                   # .update() gets called in update_tab_content
    view.dark_grey          = "#000000"                        # for CustomContainer & HeaderContainer
    view.team_logos_path    = "/fake/team_logos"               # for gen_team_logo_cell
    view.sponsor_logos_path = "/fake/sponsor_logos"            # for gen_sponsor_logo_cell
    view.flags_small_path   = "/fake/flags"                    # for gen_flag_cell (unused here)
    return view

def make_staff_df():
    """One-row staff grid with all five roles filled."""
    cols = [
        "team",
        "team_principal",
        "driver1",
        "driver2",
        "technical_director",
        "commercial_manager"
    ]
    data = [["Team A", "TP A", "D1 A", "D2 A", "TD A", "CM A"]]
    return pd.DataFrame(data, columns=cols)

def make_sponsor_df(this_year_name="Sponsor X", next_year_name=None):
    """One-row sponsor grid. Column name must match SponsorTypes.TITLE.value."""
    col = ["Team", SponsorTypes.TITLE.value]
    data = [["Team A", this_year_name]]
    df = pd.DataFrame(data, columns=col)
    # Announced next-year is a deep copy with possibly a None
    df_next = pd.DataFrame([[ "Team A", next_year_name ]], columns=col)
    return df, df_next

def test_update_page_initial_staff_grid(dummy_view):
    page = GridPage(dummy_view)

    staff_now   = make_staff_df()
    staff_next  = make_staff_df()
    sponsors_now, sponsors_next = make_sponsor_df(this_year_name="X", next_year_name="Y")

    # Call update_page for year=2025
    page.update_page(
        year=2025,
        grid_this_year_df=staff_now,
        grid_next_year_announced_df=staff_next,
        sponsors_this_year_df=sponsors_now,
        sponsors_next_year_announced_df=sponsors_next
    )

    # Tabs relabeled correctly
    assert page.current_year_tab.text == "2025"
    assert page.next_year_tab.text    == "2026"

    # By default, staff grid is active:
    assert page.staff_button_container.data   == "active"
    assert page.sponsor_button_container.data == "inactive"

    # The tables themselves should exist
    assert hasattr(page, "grid_this_year_table")
    assert hasattr(page, "grid_next_year_table")

    # And update_tab_content() should have called main_app.update()
    assert dummy_view.main_app.updated is True

def test_show_sponsor_grid_switches_and_renders(dummy_view):
    page = GridPage(dummy_view)

    # Prepare data: staff grids (not used here), and sponsors for this and next year
    staff_now  = make_staff_df()
    staff_next = make_staff_df()
    sponsors_now, sponsors_next = make_sponsor_df(this_year_name="TitleCo", next_year_name=None)

    page.update_page(
        year=2025,
        grid_this_year_df=staff_now,
        grid_next_year_announced_df=staff_next,
        sponsors_this_year_df=sponsors_now,
        sponsors_next_year_announced_df=sponsors_next
    )
    # Reset the flag so we can catch the next update()
    dummy_view.main_app.updated = False

    # Switch to sponsors
    page.show_sponsor_grid()

    # Button states flipped
    assert page.sponsor_button_container.data == "active"
    assert page.staff_button_container.data   == "inactive"

    # update_tab_content() invoked again
    assert dummy_view.main_app.updated is True

    # Inspect the first row of the "this year" sponsor table:
    rows = page.grid_this_year_table.data_table.rows
    assert len(rows) == 1
    cells = rows[0].cells

    # The second cell should be a DataCell whose content is a Row including an Image (the sponsor logo)
    cell_content = cells[1].content  # sponsor_logo_col_idx == 1
    assert isinstance(cell_content, ft.Row)
    assert any(isinstance(ctrl, ft.Image) for ctrl in cell_content.controls)

def test_tab_content_controls(dummy_view):
    """Ensure update_tab_content wires the filter buttons and ListView into each tab."""
    page = GridPage(dummy_view)
    staff_now, staff_next = make_staff_df(), make_staff_df()
    sponsors_now, sponsors_next = make_sponsor_df("X", "Y")
    page.update_page(2025, staff_now, staff_next, sponsors_now, sponsors_next)

    # Grab the content of the current-year tab
    column = page.current_year_tab.content.content
    # First control: the filter-buttons Container
    assert column.controls[0].content is page.filter_buttons
    # Second control: the ListView of the staff-table
    assert column.controls[1] is page.grid_this_year_table.list_view
