from collections import defaultdict
from typing import Any

from app.models.state import GameState
from app.models.finance import TransactionCategory


def build_finance_report(state: GameState) -> dict[str, Any]:
    transactions = state.finance.transactions

    income_total = sum(t.amount for t in transactions if t.amount > 0)
    expense_total = sum(-t.amount for t in transactions if t.amount < 0)
    net_profit_loss = income_total - expense_total
    transport_total = sum(-t.amount for t in transactions if t.category == TransactionCategory.TRANSPORT and t.amount < 0)
    workforce_total = sum(-t.amount for t in transactions if t.category == TransactionCategory.WORKFORCE_WAGES and t.amount < 0)
    engine_supplier_total = sum(-t.amount for t in transactions if t.category == TransactionCategory.ENGINE_SUPPLIER and t.amount < 0)
    tyre_supplier_total = sum(-t.amount for t in transactions if t.category == TransactionCategory.TYRE_SUPPLIER and t.amount < 0)
    sponsorship_total = sum(t.amount for t in transactions if t.category == TransactionCategory.SPONSORSHIP and t.amount > 0)

    per_track = defaultdict(lambda: {"track": "", "country": "Unknown", "income": 0, "expense": 0, "net": 0})
    for t in transactions:
        if not t.event_name:
            continue
        key = t.event_name
        row = per_track[key]
        row["track"] = t.event_name
        row["country"] = t.circuit_country or "Unknown"
        if t.amount >= 0:
            row["income"] += t.amount
        else:
            row["expense"] += -t.amount
        row["net"] = row["income"] - row["expense"]

    track_profit_loss = sorted(
        per_track.values(),
        key=lambda r: r["net"],
        reverse=True,
    )

    return {
        "summary": {
            "income_total": income_total,
            "expense_total": expense_total,
            "net_profit_loss": net_profit_loss,
            "transport_total": transport_total,
            "workforce_total": workforce_total,
            "engine_supplier_total": engine_supplier_total,
            "tyre_supplier_total": tyre_supplier_total,
            "sponsorship_total": sponsorship_total,
        },
        "track_profit_loss": track_profit_loss,
    }
