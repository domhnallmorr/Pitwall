from app.models.state import GameState
from app.models.calendar import EventType
from app.core.rollover import SeasonRolloverManager
from app.core.transport import TransportManager
from app.core.transfers import TransferManager
from app.core.management_transfers import CommercialManagerTransferManager, TechnicalDirectorTransferManager
from app.core.ai_car_development import AICarDevelopmentManager
from app.core.player_car_development import PlayerCarDevelopmentManager
from app.core.testing import TestSessionManager
from app.models.email import EmailCategory

class GameEngine:
    """
    The main orchestrator for game progression.
    """
    def __init__(self):
        self.rollover_manager = SeasonRolloverManager()
        self.transport_manager = TransportManager()
        self.transfer_manager = TransferManager()
        self.cm_transfer_manager = CommercialManagerTransferManager()
        self.td_transfer_manager = TechnicalDirectorTransferManager()
        self.ai_car_development_manager = AICarDevelopmentManager()
        self.player_car_development_manager = PlayerCarDevelopmentManager()
        self.test_session_manager = TestSessionManager()

    def advance_week(self, state: GameState) -> dict:
        """
        Advances the game by one week.
        Returns a summary of what happened.
        """
        state.calendar.advance_week()

        # Process weekly finances
        self._process_weekly_finances(state)

        # Publish any scheduled announcements for this week.
        state.publish_queued_emails()
        self.transfer_manager.publish_due_announcements(state)
        self.cm_transfer_manager.publish_due_announcements(state)
        self.td_transfer_manager.publish_due_announcements(state)
        self.ai_car_development_manager.apply_for_week(state)

        # Check for season end
        if state.calendar.season_over:
            rollover_info = self.rollover_manager.process_rollover(state)
            summary = self.get_week_summary(state)
            summary["season_rollover"] = True
            summary["rollover_info"] = rollover_info
            return summary

        return self.get_week_summary(state)

    def get_week_summary(self, state: GameState) -> dict:
        """Returns current state summary without advancing time."""
        event = state.calendar.current_event
        event_active = False
        button_text = "ADVANCE"

        if event:
            event_id = f"{event.week}_{event.name}"
            if event_id not in state.events_processed:
                event_active = True
                if event.type == EventType.RACE:
                    button_text = "GO TO RACE"
                else:
                    button_text = "GO TO TEST"

        return {
            "week": state.calendar.current_week,
            "year": state.year,
            "new_date_display": state.week_display,
            "next_event_display": state.next_event_display,
            "event_active": event_active,
            "button_text": button_text,
            "balance": state.finance.balance
        }

    def handle_event_action(self, state: GameState, action: str, test_kms: int | None = None) -> dict:
        """
        Handles actions like 'skip' or 'attend' for the current event.
        Returns the updated week summary.
        """
        event = state.calendar.current_event
        if event:
            event_id = f"{event.week}_{event.name}"
            if event_id not in state.events_processed:
                attended = action == "attend"
                charge = self.transport_manager.charge_for_event(state, event, attended=attended)
                if charge:
                    state.add_email(
                        sender="Logistics Coordinator",
                        subject=f"Transport Confirmed: {charge.event_name}",
                        body=(
                            f"Transport for {charge.event_name} has been confirmed.\n\n"
                            f"Destination: {charge.country}\n"
                            f"Cost: ${charge.applied_cost:,}"
                        ),
                        category=EmailCategory.GENERAL,
                    )
                if event.type == EventType.TEST:
                    self.test_session_manager.process_test_session(
                        state,
                        event,
                        player_attended=attended,
                        player_kms=int(test_kms or 0),
                    )
                state.events_processed.append(event_id)

        return self.get_week_summary(state)

    def _process_weekly_finances(self, state: GameState):
        """Process non-race recurring finances."""
        self.player_car_development_manager.process_week(state)
