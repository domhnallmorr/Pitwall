from app.models.email import EmailCategory
from app.models.state import GameState


def send_facilities_update_email(state: GameState, ai_facilities_upgrades: list[dict]):
    if ai_facilities_upgrades:
        lines = [
            f"- {u['team_name']}: {u['old_facilities']} -> {u['new_facilities']} (+{u['increase']})"
            for u in ai_facilities_upgrades
        ]
        body = (
            f"The following AI teams upgraded facilities for {state.year}:\n\n"
            + "\n".join(lines)
        )
    else:
        body = f"No AI teams upgraded facilities for {state.year}."
    state.add_email(
        sender="Competition Office",
        subject=f"Facilities Development Update: {state.year}",
        body=body,
        category=EmailCategory.SEASON,
    )


def send_ai_workforce_update_email(state: GameState, ai_workforce_updates: list[dict]):
    if ai_workforce_updates:
        lines = [
            f"- {u['team_name']}: {u['old_workforce']} -> {u['new_workforce']} ({u['delta']:+})"
            for u in ai_workforce_updates
        ]
        body = (
            f"The following AI teams adjusted workforce for {state.year}:\n\n"
            + "\n".join(lines)
        )
    else:
        body = f"No AI teams changed workforce for {state.year}."
    state.add_email(
        sender="Competition Office",
        subject=f"AI Workforce Update: {state.year}",
        body=body,
        category=EmailCategory.SEASON,
    )


def send_new_season_email(state: GameState, old_year: int, champion: str):
    state.add_email(
        sender="Board of Directors",
        subject=f"New Season: {state.year}",
        body=(
            f"The {old_year} season is over. {champion} won the Drivers' Championship.\n\n"
            f"Welcome to {state.year}! All points have been reset. A new season awaits."
        ),
        category=EmailCategory.SEASON,
    )


def send_retirement_email(state: GameState, subject: str, intro: str, retirees: list[dict]):
    if not retirees:
        return
    retired_lines = [f"- {m['name']} ({m['team_name']})" for m in retirees]
    state.add_email(
        sender="Competition Office",
        subject=subject,
        body=(intro + "\n\n" + "\n".join(retired_lines)),
        category=EmailCategory.SEASON,
    )


def send_new_drivers_email(state: GameState, new_entrants: list[dict]):
    if not new_entrants:
        return
    entrant_lines = [f"- {d['name']} ({d['country']})" for d in new_entrants]
    state.add_email(
        sender="Competition Office",
        subject=f"New Drivers Entering {state.year}",
        body=(
            f"The following drivers have entered the championship pool for {state.year}:\n\n"
            + "\n".join(entrant_lines)
        ),
        category=EmailCategory.SEASON,
    )


def send_new_title_sponsors_email(state: GameState, new_title_sponsors: list[dict]):
    if not new_title_sponsors:
        return
    sponsor_lines = [f"- {s['name']} (wealth {s['wealth']})" for s in new_title_sponsors]
    state.add_email(
        sender="Competition Office",
        subject=f"New Title Sponsors Entering {state.year}",
        body=(
            f"The following title sponsors have entered the market for {state.year}:\n\n"
            + "\n".join(sponsor_lines)
        ),
        category=EmailCategory.SEASON,
    )


def publish_week_one_signings_email(state: GameState, signings: list[dict]):
    if not signings:
        return
    signing_lines = [f"- {s['team_name']}: {s['driver_name']} ({s['seat']})" for s in signings]
    state.queue_email(
        sender="Driver Market Desk",
        subject=f"Driver Signings: {state.year}",
        body=(
            f"Completed signings for Week 1 of {state.year}:\n\n"
            + "\n".join(signing_lines)
        ),
        week=1,
        year=state.year,
        category=EmailCategory.SEASON,
    )
    state.publish_queued_emails(week=1, year=state.year)


def send_retirement_watch_email(state: GameState, final_season_drivers: list[dict]):
    if not final_season_drivers:
        return
    lines = [f"- {d['name']} ({d['team_name']}), age {d['age']}" for d in final_season_drivers]
    state.add_email(
        sender="Competition Office",
        subject=f"Retirement Watch: {state.year} Final Seasons",
        body=(
            "The following drivers have announced this will be their final season:\n\n"
            + "\n".join(lines)
        ),
        category=EmailCategory.SEASON,
    )
