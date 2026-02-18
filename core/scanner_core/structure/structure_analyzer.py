from typing import Dict, Optional

from core.scanner_core.state_machine.states import ScenarioState
from core.scanner_core.structure.structure_builder import StructureBuilder


class StructureAnalyzer:

    MIN_CORRECTION_PERCENT = 30
    MAX_CORRECTION_PERCENT = 80

    def __init__(self):
        self._builder = StructureBuilder()

    # ==========================================================

    def analyze(
        self,
        symbol: str,
        market_data: Dict,
        impulse_data: Dict,
        context_data: Dict,
        market_context,
    ) -> Dict:

        if not market_context or market_context.validity.name != "VALID":
            return {"direction": None, "phase": None}

        direction = self._determine_direction(market_context)

        if not direction:
            return {"direction": None, "phase": None}

        candles_1h = impulse_data.get("candles", [])

        if not candles_1h:
            return {"direction": None, "phase": None}

        if direction == "LONG":
            impulse = self._builder.find_long_impulse(candles_1h)
        else:
            impulse = self._builder.find_short_impulse(candles_1h)

        if not impulse:
            return {
                "direction": direction,
                "phase": ScenarioState.TREND_ACTIVE,
            }

        retrace_percent = self._calculate_retracement_percent(
            impulse,
            market_data,
            direction,
        )

        payload = impulse.copy()
        payload["retrace_percent"] = retrace_percent
        payload["direction"] = direction
        payload["candles_1h"] = candles_1h

        if retrace_percent > self.MAX_CORRECTION_PERCENT:
            return {
                "direction": direction,
                "phase": ScenarioState.CANCELLED,
                "payload": payload,
            }

        if retrace_percent >= self.MIN_CORRECTION_PERCENT:
            return {
                "direction": direction,
                "phase": ScenarioState.CORRECTION,
                "payload": payload,
            }

        return {
            "direction": direction,
            "phase": ScenarioState.IMPULSE,
            "payload": payload,
        }

    # ==========================================================

    def _determine_direction(self, market_context):
        if market_context.phase.name == "TREND_UP":
            return "LONG"
        if market_context.phase.name == "TREND_DOWN":
            return "SHORT"
        return None

    # ==========================================================

    def _calculate_retracement_percent(
        self,
        impulse: Dict,
        market_data: Dict,
        direction: str,
    ) -> float:

        candles_5m = market_data.get("candles", [])
        if not candles_5m:
            return 0

        current_price = candles_5m[-1]["close"]

        start = impulse["start_price"]
        end = impulse["end_price"]

        if direction == "LONG":
            retrace = (end - current_price) / (end - start)
        else:
            retrace = (current_price - end) / (start - end)

        return max(0, retrace * 100)
