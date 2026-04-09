import random
from typing import Any, Dict

from app.core.transfers import TransferManager
from app.models.email import EmailCategory
from app.models.state import GameState


class PlayerDriverNegotiationManager:
    def __init__(self):
        self.transfer_manager = TransferManager()

    def submit_offer(
        self,
        state: GameState,
        outgoing_driver_id: int,
        incoming_driver_id: int,
        salary_offer: int,
        contract_length: int,
    ) -> Dict[str, Any]:
        player_team = state.player_team
        if player_team is None:
            raise ValueError("No player team assigned")
        if contract_length not in {1, 2, 3}:
            raise ValueError("Contract length must be 1, 2, or 3 years")
        if salary_offer < 0:
            raise ValueError("Salary offer must be zero or greater")

        seat, seat_label, outgoing = self.transfer_manager._get_player_seat_and_driver(  # noqa: SLF001
            state,
            outgoing_driver_id,
            player_team.id,
        )
        if seat is None or outgoing is None:
            raise ValueError("Driver is not in a player team race seat")
        if outgoing.contract_length >= 2:
            raise ValueError("Driver has 2 or more years remaining on contract")

        candidates = self.transfer_manager.get_player_replacement_candidates(state, outgoing_driver_id)
        incoming = next((d for d in candidates if d.id == incoming_driver_id), None)
        if incoming is None:
            raise ValueError("Selected driver is not available for negotiation")

        accepted, interest_band, score = self._evaluate_offer(state, incoming, salary_offer, contract_length)
        current_team_name = next((team.name for team in state.teams if team.id == incoming.team_id), None)
        market_salary = self._market_salary(incoming)
        offer_summary = {
            "team_id": player_team.id,
            "team_name": player_team.name,
            "seat": seat,
            "seat_label": seat_label,
            "driver_id": incoming.id,
            "driver_name": incoming.name,
            "salary": salary_offer,
            "contract_length": contract_length,
            "interest_band": interest_band,
            "score": score,
            "current_team_name": current_team_name,
            "market_salary": market_salary,
        }

        if not accepted:
            return {
                "accepted": False,
                "interest_band": interest_band,
                "message": self._rejection_message(incoming, current_team_name, interest_band),
                **offer_summary,
            }

        announced = list(state.announced_ai_signings)
        existing = next(
            (signing for signing in announced if signing["team_id"] == player_team.id and signing["seat"] == seat),
            None,
        )
        if existing:
            announced.remove(existing)

        signing = {
            "team_id": player_team.id,
            "team_name": player_team.name,
            "seat": seat,
            "seat_label": seat_label,
            "driver_id": incoming.id,
            "driver_name": incoming.name,
            "announce_week": state.calendar.current_week,
            "announce_year": state.year,
            "status": "announced",
            "origin": "player_offer",
            "salary": salary_offer,
            "contract_length": contract_length,
        }
        announced.append(signing)
        state.announced_ai_signings = announced
        self.transfer_manager.recompute_ai_signings(state)

        state.add_email(
            sender="Driver Market Desk",
            subject=f"Driver Offer Accepted: {incoming.name}",
            body=(
                f"{incoming.name} has accepted your offer to join {player_team.name} for next season "
                f"({state.year + 1}) as {seat_label}. Agreed salary: ${salary_offer:,} over {contract_length} year(s)."
            ),
            category=EmailCategory.SEASON,
        )

        return {
            "accepted": True,
            "interest_band": interest_band,
            "message": (
                f"{incoming.name} has accepted your offer and will join {player_team.name} next season "
                f"on a {contract_length}-year deal."
            ),
            **offer_summary,
        }

    def _evaluate_offer(
        self,
        state: GameState,
        driver: Any,
        salary_offer: int,
        contract_length: int,
    ) -> tuple[bool, str, int]:
        player_team = state.player_team
        player_desirability = self.transfer_manager._team_desirability(state, player_team) if player_team else 50  # noqa: SLF001
        current_team = next((team for team in state.teams if team.id == driver.team_id), None)
        current_desirability = self.transfer_manager._team_desirability(state, current_team) if current_team else 50  # noqa: SLF001

        score = 40
        if driver.team_id is None:
            score += 22
        elif driver.contract_length == 1:
            score += 6

        score += max(-24, min(24, round((player_desirability - current_desirability) * 0.55)))

        market_salary = self._market_salary(driver)
        salary_delta = salary_offer - market_salary
        if market_salary > 0:
            salary_delta_ratio = salary_delta / market_salary
            score += max(-18, min(26, round(salary_delta_ratio * 28)))

        score += {1: 0, 2: 4, 3: 7}.get(contract_length, 0)

        if driver.speed >= 95:
            score -= 18
        elif driver.speed >= 85:
            score -= 10
        elif driver.speed >= 75:
            score -= 4

        if current_team is not None and current_desirability >= player_desirability + 10:
            score -= 10
        if driver.team_id is None:
            score += 4

        score += random.randint(-8, 8)
        interest_band = self._interest_band(score)
        return score >= 50, interest_band, score

    def _market_salary(self, driver: Any) -> int:
        current_wage = abs(int(getattr(driver, "wage", 0) or 0))
        if current_wage > 0:
            return current_wage
        return max(250_000, int((getattr(driver, "speed", 50) or 50) * 20_000))

    def _interest_band(self, score: int) -> str:
        if score >= 75:
            return "Very Interested"
        if score >= 60:
            return "Interested"
        if score >= 45:
            return "Unsure"
        if score >= 30:
            return "Unlikely"
        return "Not Interested"

    def _rejection_message(self, driver: Any, current_team_name: str | None, interest_band: str) -> str:
        if current_team_name:
            return (
                f"{driver.name} turned the offer down. Interest level: {interest_band}. "
                f"They are not prepared to leave {current_team_name} on those terms."
            )
        return f"{driver.name} turned the offer down. Interest level: {interest_band}."
