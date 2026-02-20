from pydantic import BaseModel, Field
from typing import List
from enum import Enum


class TransactionCategory(str, Enum):
    DRIVER_WAGES = "driver_wages"
    PRIZE_MONEY = "prize_money"
    TRANSPORT = "transport"
    CRASH_DAMAGE = "crash_damage"
    SPONSORSHIP = "sponsorship"
    TRANSFER_FEE = "transfer_fee"
    DEVELOPMENT = "development"
    FACILITIES = "facilities"
    OTHER = "other"


class Transaction(BaseModel):
    week: int
    year: int
    amount: int  # Positive = income, negative = expense
    category: TransactionCategory
    description: str
    event_name: str | None = None
    event_type: str | None = None
    circuit_country: str | None = None


class Finance(BaseModel):
    balance: int = 0
    transactions: List[Transaction] = Field(default_factory=list)
    prize_money_entitlement: int = 0
    prize_money_paid: int = 0
    prize_money_races_paid: int = 0
    prize_money_total_races: int = 0

    def add_transaction(self, week: int, year: int, amount: int,
                        category: TransactionCategory, description: str,
                        event_name: str | None = None,
                        event_type: str | None = None,
                        circuit_country: str | None = None):
        """Record a transaction and update the balance."""
        self.transactions.append(Transaction(
            week=week, year=year, amount=amount,
            category=category,
            description=description,
            event_name=event_name,
            event_type=event_type,
            circuit_country=circuit_country,
        ))
        self.balance += amount
