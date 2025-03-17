'''
Typed dict that gets passed to the view to update UI
'''
from typing import TypedDict, List, Union

class FinanceData(TypedDict):
    profit: int
    title_sponsor: str
    title_sponsor_value: int
    other_sponsorship: int
    prize_money: int
    drivers_payments: int
    total_income: int
    total_staff_costs_per_year: int
    drivers_salary: int
    technical_director_salary: int
    commercial_manager_salary: int
    engine_supplier_cost: int
    race_costs: int
    car_development_costs: int
    total_expenditure: int
    balance_history: List[Union[int, float]]
    balance_history_dates: List[Union[int, float]]