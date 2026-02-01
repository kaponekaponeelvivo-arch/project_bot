# core/scanner_core/scenario/scenario_manager.py
from typing import Dict, Optional

from .scenario import Scenario
from core.scanner_core.state_machine import ScenarioState


class ScenarioManager:
    """
    Manages scenarios lifecycle.
    One scenario per symbol.
    """

    def __init__(self) -> None:
        self._scenarios: Dict[str, Scenario] = {}

    def get(self, symbol: str) -> Optional[Scenario]:
        return self._scenarios.get(symbol)

    def create(self, symbol: str, direction: str) -> Scenario:
        """
        Create new scenario from IDLE.
        """
        scenario = Scenario(
            symbol=symbol,
            direction=direction,
            state=ScenarioState.TREND_ACTIVE,
        )
        self._scenarios[symbol] = scenario
        return scenario

    def remove(self, symbol: str) -> None:
        """
        Remove scenario completely (after completion/cancel).
        """
        self._scenarios.pop(symbol, None)

    def all(self) -> Dict[str, Scenario]:
        return self._scenarios
