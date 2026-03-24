import random


def build_announcement_window(state):
    max_week = max((e.week for e in state.calendar.events), default=state.calendar.current_week)
    race_weeks = sorted(
        e.week for e in state.calendar.events if getattr(e.type, "value", e.type) == "RACE"
    )
    first_race_week = race_weeks[0] if race_weeks else state.calendar.current_week
    min_announce_week = max(state.calendar.current_week + 1, first_race_week + 1)
    min_announce_week = min(min_announce_week, max_week)
    return min_announce_week, max_week


def choose_announce_week(state):
    min_announce_week, max_week = build_announcement_window(state)
    return random.randint(min_announce_week, max_week)
