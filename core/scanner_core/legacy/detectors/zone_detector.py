from typing import Optional, List, Dict, Any

from core.scanner_core.events import Event, EventType
from core.scanner_core.events.event_bus import EventBus
from core.scanner_core.state_machine.states import ScenarioState


class ZoneDetector:
    """
    Detects FVG or fallback fib zone during CORRECTION phase.
    """

    def analyze(
        self,
        symbol: str,
        impulse_data: dict,      # 1H
        scenario,
        event_bus: EventBus,
    ) -> None:

        if scenario.state != ScenarioState.CORRECTION:
            return

        impulse_event = next(
            (e for e in reversed(scenario.events)
             if e.type == EventType.CORRECTION_STARTED),
            None,
        )

        if not impulse_event:
            return

        impulse_high = impulse_event.payload.get("impulse_high")
        impulse_low = impulse_event.payload.get("impulse_low")

        candles: List[dict] = impulse_data.get("candles", [])
        if len(candles) < 3:
            return

        # ===============================
        # 1️⃣ Try FVG (3-candle gap)
        # ===============================
        fvg_zone = self._find_fvg(candles)

        if fvg_zone:
            payload = impulse_event.payload.copy()
            payload["zone_type"] = "FVG"
            payload["zone_from"] = fvg_zone["low"]
            payload["zone_to"] = fvg_zone["high"]

            event_bus.publish(
                Event(
                    type=EventType.ZONE_REACTED,
                    symbol=symbol,
                    payload=payload,
                )
            )
            return

        # ===============================
        # 2️⃣ Fallback Fibonacci 0.618–0.782
        # ===============================
        fib_618 = impulse_low + (impulse_high - impulse_low) * 0.618
        fib_782 = impulse_low + (impulse_high - impulse_low) * 0.782

        payload = impulse_event.payload.copy()
        payload["zone_type"] = "FIB"
        payload["zone_from"] = round(fib_618, 6)
        payload["zone_to"] = round(fib_782, 6)

        event_bus.publish(
            Event(
                type=EventType.ZONE_REACTED,
                symbol=symbol,
                payload=payload,
            )
        )

    # ==========================================================

    def _find_fvg(self, candles: List[dict]) -> Optional[Dict[str, Any]]:

        for i in range(1, len(candles) - 1):
            prev = candles[i - 1]
            curr = candles[i]
            next_c = candles[i + 1]

            if prev["high"] < next_c["low"]:
                return {
                    "low": prev["high"],
                    "high": next_c["low"],
                }

        return None
