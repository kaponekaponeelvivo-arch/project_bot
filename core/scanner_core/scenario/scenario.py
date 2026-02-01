# core/scanner_core/scenario/scenario.py
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

from core.scanner_core.state_machine import ScenarioState
from core.scanner_core.events import Event


@dataclass
class Scenario:
    """
    Scenario is a state container.
    It does not analyze market or decide transitions.
    """
    symbol: str
    direction: str                  # "LONG" or "SHORT"
    state: ScenarioState = ScenarioState.IDLE

    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    events: List[Event] = field(default_factory=list)

    # Placeholders for future layers
    impulse: Optional[object] = None
    zones: List[object] = field(default_factory=list)

    def add_event(self, event: Event) -> None:
        """
        Store event in scenario history.
        """
        self.events.append(event)
        self.updated_at = datetime.utcnow()

    def set_state(self, new_state: ScenarioState) -> None:
        """
        Update scenario state.
        """
        if self.state != new_state:
            self.state = new_state
            self.updated_at = datetime.utcnow()
