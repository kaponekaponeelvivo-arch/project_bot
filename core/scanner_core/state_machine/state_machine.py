# core/scanner_core/state_machine/state_machine.py
from typing import Optional

from .states import ScenarioState
from .transitions import TRANSITIONS
from core.scanner_core.events.event_types import EventType


class StateMachine:
    """
    Stateless state machine.
    Decides whether transition is allowed.
    """

    @staticmethod
    def transition(
        current_state: ScenarioState,
        event_type: EventType,
    ) -> Optional[ScenarioState]:
        """
        Returns new state if transition is allowed, otherwise None.
        """
        state_transitions = TRANSITIONS.get(current_state)
        if not state_transitions:
            return None

        return state_transitions.get(event_type)
