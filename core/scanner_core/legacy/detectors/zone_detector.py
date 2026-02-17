from typing import Optional, List, Dict, Any

from core.scanner_core.events import Event, EventType
from core.scanner_core.events.event_bus import EventBus
from core.scanner_core.state_machine.states import ScenarioState


class ZoneDetector:

    def analyze(
        self,
        symbol: str,
        impulse_data: dict,
        scenario,
        event_bus: EventBus,
    ) -> None:

        if scenario.state != ScenarioState.CORRECTION:
            return

        correction_event = next(
            (e for e in reversed(scenario.events)
             if e.type == EventType.CORRECTION_STARTED),
            None,
        )

        if not correction_event:
            return

        payload = correction_event.payload
        end_index = payload.get("end_index")

        candles: List[dict] = impulse_data.get("candles", [])
        if not candles or end_index is None:
            return

        # Ограничиваем поиск только зоной коррекции
        correction_candles = candles[end_index:]
        if len(correction_candles) < 3:
            return

        fvg_zone = self._find_fvg(correction_candles)

        if fvg_zone:
            new_payload = payload.copy()
            new_payload["zone_type"] = "FVG"
            new_payload["zone_from"] = fvg_zone["low"]
            new_payload["zone_to"] = fvg_zone["high"]

            event_bus.publish(
                Event(
                    type=EventType.ZONE_REACTED,
                    symbol=symbol,
                    payload=new_payload,
                )
            )
            return

        # fallback fib
        impulse_high = payload.get("impulse_high")
        impulse_low = payload.get("impulse_low")

        if impulse_high is None or impulse_low is None:
            return

        fib_618 = impulse_low + (impulse_high - impulse_low) * 0.618
        fib_782 = impulse_low + (impulse_high - impulse_low) * 0.782

        new_payload = payload.copy()
        new_payload["zone_type"] = "FIB"
        new_payload["zone_from"] = round(fib_618, 6)
        new_payload["zone_to"] = round(fib_782, 6)

        event_bus.publish(
            Event(
                type=EventType.ZONE_REACTED,
                symbol=symbol,
                payload=new_payload,
            )
        )

    def _find_fvg(self, candles: List[dict]) -> Optional[Dict[str, Any]]:

        for i in range(1, len(candles) - 1):
            prev = candles[i - 1]
            next_c = candles[i + 1]

            if prev["high"] < next_c["low"]:
                return {
                    "low": prev["high"],
                    "high": next_c["low"],
                }

        return None
