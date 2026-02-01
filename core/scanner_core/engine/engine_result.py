from dataclasses import dataclass
from typing import List

from core.scanner_core.events import Event
from core.scanner_core.state_machine import ScenarioState


@dataclass
class EngineResult:
    """
    Result of one engine cycle.
    Returned to upper layers (bot, api, tests).
    """
    symbol: str
    state: ScenarioState
    events: List[Event]
    state_changed: bool
