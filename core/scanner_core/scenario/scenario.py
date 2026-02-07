from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from core.scanner_core.state_machine.states import ScenarioState
from core.scanner_core.events import Event


@dataclass
class Scenario:
    """
    Scenario is a state container.
    FSM logic lives outside (StateMachine).
    """

    symbol: str
    direction: str
    state: ScenarioState

    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    events: List[Event] = field(default_factory=list)

    # ===============================
    # STATE MANAGEMENT
    # ===============================
    def set_state(self, new_state: ScenarioState) -> None:
        if self.state != new_state:
            self.state = new_state
            self.updated_at = datetime.utcnow()

    # ===============================
    # EVENT HISTORY
    # ===============================
    def add_event(self, event: Event) -> None:
        self.events.append(event)
        self.updated_at = datetime.utcnow()
