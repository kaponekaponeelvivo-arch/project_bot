from typing import List

from core.scanner_core.events import Event, EventType
from core.scanner_core.events.event_bus import EventBus
from core.scanner_core.zones.zone import Zone


class CancelledDetector:
    """
    Detects scenario invalidation AFTER confirmation.
    """

    def analyze(
        self,
        symbol: str,
        market_data: dict,
        direction: str,
        active_zones: list[Zone],
        event_bus: EventBus,
    ) -> None:

        candles: List[dict] = market_data.get("candles", [])
        if not candles:
            return

        last = candles[-1]

        # ===============================
        # A) Zone invalidation
        # ===============================
        for zone in active_zones:
            if direction == "LONG" and last["close"] < zone.price_from:
                event_bus.publish(
                    Event(
                        type=EventType.SCENARIO_CANCELLED,
                        symbol=symbol,
                        payload={"reason": "zone_invalidated"},
                    )
                )
                return

            if direction == "SHORT" and last["close"] > zone.price_to:
                event_bus.publish(
                    Event(
                        type=EventType.SCENARIO_CANCELLED,
                        symbol=symbol,
                        payload={"reason": "zone_invalidated"},
                    )
                )
                return

        # ===============================
        # B) Local structure break
        # ===============================
        if len(candles) < 2:
            return

        prev = candles[-2]

        if direction == "LONG" and last["close"] < prev["low"]:
            event_bus.publish(
                Event(
                    type=EventType.SCENARIO_CANCELLED,
                    symbol=symbol,
                    payload={"reason": "structure_broken"},
                )
            )

        if direction == "SHORT" and last["close"] > prev["high"]:
            event_bus.publish(
                Event(
                    type=EventType.SCENARIO_CANCELLED,
                    symbol=symbol,
                    payload={"reason": "structure_broken"},
                )
            )
