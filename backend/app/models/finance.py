from pydantic import BaseModel
from typing import List
from enum import Enum


class TransactionCategory(str, Enum):
    DRIVER_WAGES = "driver_wages"
    PRIZE_MONEY = "prize_money"
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


class Finance(BaseModel):
    balance: int = 0
    transactions: List[Transaction] = []

    def add_transaction(self, week: int, year: int, amount: int,
                        category: TransactionCategory, description: str):
        """Record a transaction and update the balance."""
        self.transactions.append(Transaction(
            week=week, year=year, amount=amount,
            category=category, description=description
        ))
        self.balance += amount
