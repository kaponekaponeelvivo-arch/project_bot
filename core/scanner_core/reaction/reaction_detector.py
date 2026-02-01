from typing import Optional

from core.scanner_core.events import Event, EventType
from core.scanner_core.events.event_bus import EventBus
from core.scanner_core.zones.zone import Zone
from core.scanner_core.zones.zone_status import ZoneStatus


class ReactionDetector:
    """
    REACTION B+ detector:
    - instant reaction (fast response with strength)
    - confirmed reaction (pause + structure)
    """

    # глубина входа в зону для instant-реакции (30%)
    MIN_PENETRATION_RATIO = 0.3

    def analyze(
        self,
        symbol: str,
        market_data: dict,
        zone: Zone,
        direction: str,
        event_bus: EventBus,
    ) -> Optional[str]:
        """
        Returns reaction_type if detected: 'instant' | 'confirmed'
        """

        if zone.status != ZoneStatus.ACTIVE:
            return None

        candles = market_data.get("candles", [])
        if len(candles) < 2:
            return None

        last = candles[-1]
        prev = candles[-2]

        price = last.get("close")
        if price is None:
            return None

        # -----------------------------------------
        # Check price inside zone
        # -----------------------------------------
        if not (zone.price_from <= price <= zone.price_to):
            return None

        zone_width = zone.price_to - zone.price_from
        if zone_width <= 0:
            return None

        penetration = abs(price - zone.price_from) / zone_width

        # =========================================
        # TYPE 1 — INSTANT REACTION
        # =========================================
        strong_body = abs(last["close"] - last["open"]) > abs(prev["close"] - prev["open"])
        correct_direction = (
            (direction == "LONG" and last["close"] > last["open"]) or
            (direction == "SHORT" and last["close"] < last["open"])
        )

        if penetration >= self.MIN_PENETRATION_RATIO and strong_body and correct_direction:
            zone.set_status(ZoneStatus.REACTED)

            event_bus.publish(
                Event(
                    type=EventType.REACTION_DETECTED,
                    symbol=symbol,
                    payload={
                        "reaction_type": "instant",
                        "zone_type": zone.zone_type.value,
                    },
                )
            )
            return "instant"

        # =========================================
        # TYPE 2 — CONFIRMED REACTION
        # =========================================
        small_range = abs(last["high"] - last["low"]) < abs(prev["high"] - prev["low"])

        if small_range and correct_direction:
            zone.set_status(ZoneStatus.REACTED)

            event_bus.publish(
                Event(
                    type=EventType.REACTION_DETECTED,
                    symbol=symbol,
                    payload={
                        "reaction_type": "confirmed",
                        "zone_type": zone.zone_type.value,
                    },
                )
            )
            return "confirmed"

        return None
