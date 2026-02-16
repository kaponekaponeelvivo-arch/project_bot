from typing import Optional, Dict, Any, List
from core.scanner_core.state_machine.states import ScenarioState
from core.scanner_core.market_context.context import ContextValidity


class StructureAnalyzer:

    IMPULSE_THRESHOLD = 0.15
    CORRECTION_THRESHOLD = 0.30
    LOOKBACK_CANDLES = 200

    # ==========================================================
    def analyze(
        self,
        symbol: str,
        market_data: dict,
        impulse_data: dict,
        context_data: dict,
        market_context,
    ) -> Dict[str, Any]:

        direction = self._determine_direction(market_context)
        if not direction:
            return {"direction": None, "phase": None}

        impulse = self._find_last_impulse(impulse_data, direction)
        if not impulse:
            return {
                "direction": direction,
                "phase": ScenarioState.TREND_ACTIVE,
            }

        current_price = market_data["candles"][-1]["close"]

        retrace_ratio = self._calculate_retracement(
            current_price=current_price,
            impulse=impulse,
            direction=direction,
        )

        payload = impulse.copy()

        payload["candles_5m"] = market_data.get("candles", [])
        payload["candles_4h"] = context_data.get("candles", [])
        payload["global_trend"] = (
            market_context.phase.name
            if market_context and market_context.validity == ContextValidity.VALID
            else None
        )
        payload["direction"] = direction
        payload["correction_start_index"] = payload["end_index"]
        payload["current_index"] = len(payload["candles_5m"]) - 1

        if retrace_ratio < self.CORRECTION_THRESHOLD:
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
    def _find_last_impulse(
        self,
        impulse_data: dict,
        direction: str,
    ) -> Optional[Dict[str, Any]]:

        candles: List[dict] = impulse_data.get("candles", [])
        if len(candles) < 20:
            return None

        candles = candles[-self.LOOKBACK_CANDLES:]

        if direction == "LONG":
            return self._find_long_impulse(candles)

        return self._find_short_impulse(candles)

    # ==========================================================
    def _find_long_impulse(self, candles: List[dict]) -> Optional[Dict[str, Any]]:

        for peak_index in range(len(candles) - 2, 10, -1):

            peak = candles[peak_index]
            peak_price = peak["high"]

            # Проверяем откат после peak
            after = candles[peak_index + 1:]
            if not after:
                continue

            min_after = min(c["low"] for c in after)
            move_after = peak_price - min_after

            if move_after <= 0:
                continue

            retrace_ratio = move_after / (peak_price - min_after + 1e-9)
            if retrace_ratio < self.CORRECTION_THRESHOLD:
                continue

            # Ищем low до peak
            before = candles[:peak_index]
            if not before:
                continue

            low_price = min(c["low"] for c in before)
            move = peak_price - low_price

            if move <= 0:
                continue

            percent = move / low_price
            if percent < self.IMPULSE_THRESHOLD:
                continue

            start_index = next(
                i for i, c in enumerate(candles[:peak_index])
                if c["low"] == low_price
            )

            return {
                "start_price": low_price,
                "end_price": peak_price,
                "move_percent": round(percent * 100, 2),
                "start_index": start_index,
                "end_index": peak_index,
                "impulse_high": peak_price,
                "impulse_low": low_price,
            }

        return None

    # ==========================================================
    def _find_short_impulse(self, candles: List[dict]) -> Optional[Dict[str, Any]]:

        for trough_index in range(len(candles) - 2, 10, -1):

            trough = candles[trough_index]
            trough_price = trough["low"]

            after = candles[trough_index + 1:]
            if not after:
                continue

            max_after = max(c["high"] for c in after)
            move_after = max_after - trough_price

            if move_after <= 0:
                continue

            retrace_ratio = move_after / (max_after - trough_price + 1e-9)
            if retrace_ratio < self.CORRECTION_THRESHOLD:
                continue

            before = candles[:trough_index]
            if not before:
                continue

            high_price = max(c["high"] for c in before)
            move = high_price - trough_price

            if move <= 0:
                continue

            percent = move / high_price
            if percent < self.IMPULSE_THRESHOLD:
                continue

            start_index = next(
                i for i, c in enumerate(candles[:trough_index])
                if c["high"] == high_price
            )

            return {
                "start_price": high_price,
                "end_price": trough_price,
                "move_percent": round(percent * 100, 2),
                "start_index": start_index,
                "end_index": trough_index,
                "impulse_high": high_price,
                "impulse_low": trough_price,
            }

        return None

    # ==========================================================
    def _calculate_retracement(self, current_price, impulse, direction):

        start = impulse["start_price"]
        end = impulse["end_price"]
        total = abs(end - start)

        if total == 0:
            return 0

        if direction == "LONG":
            retrace = end - current_price
        else:
            retrace = current_price - end

        return retrace / total
