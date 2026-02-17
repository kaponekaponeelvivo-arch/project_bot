from typing import Optional, Dict, Any, List
from core.scanner_core.state_machine.states import ScenarioState
from core.scanner_core.market_context.context import ContextValidity


class StructureAnalyzer:

    LOOKBACK_CANDLES = 300
    MIN_IMPULSE_PERCENT = 25.0
    MIN_IMPULSE_CANDLES = 15

    MIN_CORRECTION_PERCENT = 30.0
    MAX_CORRECTION_PERCENT = 80.0

    # ==========================================================

    def analyze(
        self,
        symbol: str,
        market_data: dict,     # 5M
        impulse_data: dict,    # 1H
        context_data: dict,    # 4H
        market_context,
    ) -> Dict[str, Any]:

        direction = self._determine_direction(market_context)
        if not direction:
            return {"direction": None, "phase": None}

        impulse = self._find_impulse(impulse_data, direction)
        if not impulse:
            return {
                "direction": direction,
                "phase": ScenarioState.TREND_ACTIVE,
            }

        current_price = market_data["candles"][-1]["close"]

        retrace_percent = self._calculate_retracement_percent(
            current_price=current_price,
            impulse=impulse,
            direction=direction,
        )

        # отмена при слишком глубокой коррекции
        if retrace_percent > self.MAX_CORRECTION_PERCENT:
            return {
                "direction": direction,
                "phase": ScenarioState.CANCELLED,
                "payload": impulse,
            }

        payload = impulse.copy()
        payload["direction"] = direction
        payload["retrace_percent"] = retrace_percent
        payload["candles_5m"] = market_data.get("candles", [])
        payload["candles_1h"] = impulse_data.get("candles", [])
        payload["candles_4h"] = context_data.get("candles", [])
        payload["global_trend"] = (
            market_context.phase.name
            if market_context and market_context.validity == ContextValidity.VALID
            else None
        )

        if retrace_percent < self.MIN_CORRECTION_PERCENT:
            return {
                "direction": direction,
                "phase": ScenarioState.IMPULSE,
                "payload": payload,
            }

        return {
            "direction": direction,
            "phase": ScenarioState.CORRECTION,
            "payload": payload,
        }

    # ==========================================================

    def _determine_direction(self, market_context) -> Optional[str]:

        if not market_context:
            return None

        if market_context.validity != ContextValidity.VALID:
            return None

        phase = getattr(market_context, "phase", None)
        if not phase:
            return None

        if phase.name == "TREND_UP":
            return "LONG"

        if phase.name == "TREND_DOWN":
            return "SHORT"

        return None

    # ==========================================================

    def _find_impulse(
        self,
        impulse_data: dict,
        direction: str,
    ) -> Optional[Dict[str, Any]]:

        candles: List[dict] = impulse_data.get("candles", [])
        if len(candles) < self.MIN_IMPULSE_CANDLES:
            return None

        candles = candles[-self.LOOKBACK_CANDLES:]

        if direction == "LONG":
            return self._find_long_impulse(candles)

        return self._find_short_impulse(candles)

    # ==========================================================

    def _find_long_impulse(self, candles: List[dict]) -> Optional[Dict[str, Any]]:

        lowest_index = min(range(len(candles)), key=lambda i: candles[i]["low"])
        lowest_price = candles[lowest_index]["low"]

        highest_index = max(
            range(lowest_index, len(candles)),
            key=lambda i: candles[i]["high"],
        )
        highest_price = candles[highest_index]["high"]

        if highest_index - lowest_index < self.MIN_IMPULSE_CANDLES:
            return None

        move_percent = ((highest_price - lowest_price) / lowest_price) * 100

        if move_percent < self.MIN_IMPULSE_PERCENT:
            return None

        return {
            "start_price": lowest_price,
            "end_price": highest_price,
            "move_percent": round(move_percent, 2),
            "start_index": lowest_index,
            "end_index": highest_index,
            "impulse_high": highest_price,
            "impulse_low": lowest_price,
        }

    # ==========================================================

    def _find_short_impulse(self, candles: List[dict]) -> Optional[Dict[str, Any]]:

        highest_index = max(range(len(candles)), key=lambda i: candles[i]["high"])
        highest_price = candles[highest_index]["high"]

        lowest_index = min(
            range(highest_index, len(candles)),
            key=lambda i: candles[i]["low"],
        )
        lowest_price = candles[lowest_index]["low"]

        if lowest_index - highest_index < self.MIN_IMPULSE_CANDLES:
            return None

        move_percent = ((highest_price - lowest_price) / highest_price) * 100

        if move_percent < self.MIN_IMPULSE_PERCENT:
            return None

        return {
            "start_price": highest_price,
            "end_price": lowest_price,
            "move_percent": round(move_percent, 2),
            "start_index": highest_index,
            "end_index": lowest_index,
            "impulse_high": highest_price,
            "impulse_low": lowest_price,
        }

    # ==========================================================

    def _calculate_retracement_percent(self, current_price, impulse, direction):

        start = impulse["start_price"]
        end = impulse["end_price"]
        total = abs(end - start)

        if total == 0:
            return 0.0

        if direction == "LONG":
            retrace = end - current_price
        else:
            retrace = current_price - end

        retrace_percent = (abs(retrace) / total) * 100
        return round(retrace_percent, 2)
