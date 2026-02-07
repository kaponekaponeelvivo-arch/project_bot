from typing import Optional

from core.scanner_core.state_machine.states import ScenarioState
from core.scanner_core.state_machine.transitions import TRANSITIONS
from core.scanner_core.events.event_types import EventType


class StateMachine:
    """
    Stateless finite state machine.
    Decides whether transition is allowed.
    """

    @staticmethod
    def transition(
        current_state: ScenarioState,
        event_type: EventType,
    ) -> Optional[ScenarioState]:
        transitions = TRANSITIONS.get(current_state)
        if not transitions:
            return None

        return transitions.get(event_type)
