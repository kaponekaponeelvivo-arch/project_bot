from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

from core.scanner_core.state_machine import ScenarioState, StateMachine
from core.scanner_core.events import Event, EventType


@dataclass
class Scenario:
    """
    Scenario is a state container.
    Applies FSM transitions based on incoming events.
    """

    symbol: str
    direction: str                  # "LONG" or "SHORT"
    state: ScenarioState = ScenarioState.IDLE

    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    events: List[Event] = field(default_factory=list)

    impulse: Optional[object] = None
    zones: List[object] = field(default_factory=list)

    def add_event(self, event: Event) -> None:
        self.events.append(event)
        self.updated_at = datetime.utcnow()

    def apply_event(self, event_type: EventType) -> bool:
        """
        Apply FSM transition by event type.
        Returns True if state was changed.
        """
        next_state = StateMachine.transition(self.state, event_type)
        if next_state and next_state != self.state:
            self.state = next_state
            self.updated_at = datetime.utcnow()
            return True

        return False
