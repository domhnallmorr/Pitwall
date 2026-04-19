from typing import Any

from app.models.calendar import EventType
from app.models.email import EmailCategory
from app.models.finance import TransactionCategory
from app.models.state import GameState

HOSPITALITY_COST = 100_000
HOSPITALITY_PROGRESS_BONUS = 1.0


def _current_week_event(state: GameState):
    return next(
        (event for event in state.calendar.events if event.week == state.calendar.current_week),
        None,
    )


def _next_race_event(state: GameState):
    return next(
        (
            event
            for event in state.calendar.events
            if event.type == EventType.RACE and event.week >= state.calendar.current_week
        ),
        None,
    )


def _discard_stale_booking(state: GameState) -> None:
    pending = state.pending_hospitality_event
    if pending and (
        pending.get("year", state.year) < state.year
        or (
            pending.get("year", state.year) == state.year
            and pending.get("week", 0) < state.calendar.current_week
        )
    ):
        state.pending_hospitality_event = None


def get_hospitality_status(state: GameState, target_type: str, *, active_negotiation: bool) -> dict[str, Any]:
    _discard_stale_booking(state)
    target_event = _next_race_event(state)
    pending = state.pending_hospitality_event

    if not active_negotiation:
        return {
            "available": False,
            "booked": False,
            "cost": HOSPITALITY_COST,
            "progress_bonus": HOSPITALITY_PROGRESS_BONUS,
            "reason": "No active negotiation available to invite.",
        }

    if target_event is None:
        return {
            "available": False,
            "booked": False,
            "cost": HOSPITALITY_COST,
            "progress_bonus": HOSPITALITY_PROGRESS_BONUS,
            "reason": "No upcoming race is available for hospitality booking.",
        }

    if pending:
        if pending.get("target_type") == target_type:
            return {
                "available": False,
                "booked": True,
                "cost": HOSPITALITY_COST,
                "progress_bonus": HOSPITALITY_PROGRESS_BONUS,
                "reason": f"Hospitality is already booked for {pending.get('event_name')} (Week {pending.get('week')}).",
                "event_name": pending.get("event_name"),
                "event_week": pending.get("week"),
            }
        return {
            "available": False,
            "booked": False,
            "cost": HOSPITALITY_COST,
            "progress_bonus": HOSPITALITY_PROGRESS_BONUS,
            "reason": f"A hospitality event is already booked for {pending.get('event_name')} (Week {pending.get('week')}).",
            "event_name": pending.get("event_name"),
            "event_week": pending.get("week"),
        }

    return {
        "available": True,
        "booked": False,
        "cost": HOSPITALITY_COST,
        "progress_bonus": HOSPITALITY_PROGRESS_BONUS,
        "reason": None,
        "event_name": target_event.name,
        "event_week": target_event.week,
    }


def book_hospitality(state: GameState, target_type: str, *, target_name: str) -> dict[str, Any]:
    _discard_stale_booking(state)
    status = get_hospitality_status(state, target_type, active_negotiation=True)
    if not status["available"]:
        raise ValueError(status["reason"])

    target_event = _next_race_event(state)
    circuit = next((c for c in state.circuits if c.name == target_event.name), None)
    state.finance.add_transaction(
        week=state.calendar.current_week,
        year=state.year,
        amount=-HOSPITALITY_COST,
        category=TransactionCategory.HOSPITALITY,
        description=f"Hospitality booked for {target_name} at {target_event.name}",
        event_name=target_event.name,
        event_type=target_event.type.value,
        circuit_country=circuit.country if circuit else None,
    )
    state.pending_hospitality_event = {
        "target_type": target_type,
        "target_name": target_name,
        "event_name": target_event.name,
        "week": target_event.week,
        "year": state.year,
        "cost": HOSPITALITY_COST,
        "progress_bonus": HOSPITALITY_PROGRESS_BONUS,
    }
    state.add_email(
        sender="Commercial Department",
        subject=f"Hospitality Booked: {target_name}",
        body=(
            f"Hospitality has been booked for {target_name} at {target_event.name} (Week {target_event.week}).\n\n"
            f"Cost: ${HOSPITALITY_COST:,}\n"
            f"Negotiation boost queued for after the race: +{HOSPITALITY_PROGRESS_BONUS:.1f} boxes"
        ),
        category=EmailCategory.GENERAL,
    )
    return get_hospitality_status(state, target_type, active_negotiation=True)


def pop_hospitality_bonus(state: GameState, target_type: str) -> dict[str, Any] | None:
    _discard_stale_booking(state)
    pending = state.pending_hospitality_event
    if not pending:
        return None
    if pending.get("target_type") != target_type:
        return None
    if pending.get("week") != state.calendar.current_week or pending.get("year") != state.year:
        return None
    state.pending_hospitality_event = None
    return pending
