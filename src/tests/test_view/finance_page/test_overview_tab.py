import pytest
import flet as ft
import pandas as pd
import types
from matplotlib.ticker import FuncFormatter

import pw_view.finance_page.overview_tab as ov_mod

# Dummy classes to stub dependencies
class DummyCC:
    def __init__(self, view, content, expand=False):
        self.view = view
        self.content = content
        self.expand = expand

class DummyHC:
    def __init__(self, view, title):
        self.view = view
        self.title = title

class DummyCanvas:
    def __init__(self):
        self.draw_calls = 0
    def draw(self):
        self.draw_calls += 1

class DummyYAxis:
    def __init__(self):
        self.formatter = None
    def set_major_formatter(self, fmt):
        self.formatter = fmt

class DummyAxes:
    def __init__(self):
        self.plot_calls = []
        self.yaxis = DummyYAxis()
        self.xlabel = None
        self.ylabel = None
    def set_xlabel(self, label):
        self.xlabel = label
    def set_ylabel(self, label):
        self.ylabel = label
    def plot(self, x, y, linestyle=None, color=None):
        self.plot_calls.append({"x": x, "y": y, "linestyle": linestyle, "color": color})

class DummyFig:
    def __init__(self):
        self.canvas = DummyCanvas()
    def tight_layout(self):
        pass
    def subplots_adjust(self, **kwargs):
        pass

class DummyMatplotlibChart:
    def __init__(self, fig, expand=True, transparent=False, original_size=True):
        self.fig = fig
        self.expand = expand
        self.transparent = transparent
        self.original_size = original_size

@pytest.fixture(autouse=True)
def patch_dependencies(monkeypatch):
    # Stub out custom_container
    monkeypatch.setattr(ov_mod.custom_container, 'CustomContainer', DummyCC)
    monkeypatch.setattr(ov_mod.custom_container, 'HeaderContainer', DummyHC)
    # Stub out matplotlib subplots
    fig = DummyFig()
    axs = DummyAxes()
    monkeypatch.setattr(ov_mod.plt, 'subplots', lambda *args, **kwargs: (fig, axs))
    # Stub out MatplotlibChart
    monkeypatch.setattr(ov_mod, 'MatplotlibChart', DummyMatplotlibChart)
    return {'fig': fig, 'axs': axs}


def test_update_tab_sets_values_and_updates_chart(patch_dependencies):
    """update_tab should update all text widgets and refresh the history chart."""
    fig = patch_dependencies['fig']
    axs = patch_dependencies['axs']
    # Create a minimal view stub
    view = object()
    tab = ov_mod.OverviewTab(view)

    # Sample data input
    data = {
        'profit': 123456,
        'title_sponsor': 'ACME',
        'title_sponsor_value': 10000,
        'other_sponsorship': 2000,
        'prize_money': 3000,
        'drivers_payments': 4000,
        'total_income': 15000,
        'total_staff_costs_per_year': 5000,
        'drivers_salary': 6000,
        'technical_director_salary': 7000,
        'commercial_manager_salary': 8000,
        'engine_supplier_cost': 9000,
        'tyre_supplier_cost': 10000,
        'race_costs': 11000,
        'damage_costs': 12000,
        'car_development_costs': 13000,
        'total_expenditure': 14000,
        'balance_history': [1, 2, 3],
        'balance_history_dates': [10, 20, 30],
        'summary_df': pd.DataFrame()
    }

    tab.update_tab(data)

    # Verify text values
    assert tab.profit_text.value == "Profit/Loss This Season: $123,456"
    assert tab.title_sponsor_text.value == "Title Sponsor: ACME"
    assert tab.title_sponsor_value_text.value == "Title Sponsorship: $10,000"
    assert tab.sponsor_income_text.value == "Other Sponsorship: $2,000"
    assert tab.prize_money_income_text.value == "Prize Money: $3,000"
    assert tab.drivers_payments_text.value == "Drivers Payments: $4,000"
    assert tab.total_income_text.value == "Total: $15,000"
    assert tab.staff_costs_text.value == "Staff Costs: $5,000"
    assert tab.drivers_salary_text.value == "Drivers Salary: $6,000"
    assert tab.technical_director_salary_text.value == "Technical Director: $7,000"
    assert tab.commercial_manager_salary_text.value == "Commercial Manager: $8,000"
    assert tab.engine_supplier_cost_text.value == "Engine Supplier: $9,000"
    assert tab.tyre_supplier_cost_text.value == "Tyre Supplier: $10,000"
    assert tab.race_costs_text.value == "Transport Costs: $11,000 (Estimated) (per race)"
    assert tab.damage_costs_text.value == "Damage Costs: $12,000 (To Date)"
    assert tab.car_development_costs_text.value == "Car Development Costs: $13,000 (To Date)"
    assert tab.total_expenditure_text.value == "Total: $14,000 (To Date)"

    # Verify chart update logic
    assert axs.plot_calls == [{
        'x': [10, 20, 30],
        'y': [1, 2, 3],
        'linestyle': '-',
        'color': '#A0CAFD'
    }]

    # Verify formatter is correctly bound to the instance method
    fmt = axs.yaxis.formatter
    assert isinstance(fmt, FuncFormatter)
    bound_method = fmt.func
    assert hasattr(bound_method, '__self__') and bound_method.__self__ is tab
    assert hasattr(bound_method, '__func__') and bound_method.__func__ is ov_mod.OverviewTab.balance_formatter

    # Verify canvas draw
    assert fig.canvas.draw_calls == 1
