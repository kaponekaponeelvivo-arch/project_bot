from core.scanner_core.events import Event, EventType
from core.scanner_core.events.event_bus import EventBus
from .zone import Zone
from .zone_types import ZoneType
from .zone_status import ZoneStatus


class ZoneDetector:
    """
    Creates zones on CORRECTION.
    MVP version.
    """

    def __init__(self) -> None:
        self._zones: list[Zone] = []

    def analyze(
        self,
        symbol: str,
        market_data: dict,
        direction: str,
        event_bus: EventBus,
    ) -> None:
        """
        Create zone based on last impulse correction.
        """

        candles = market_data.get("candles", [])
        if len(candles) < 3:
            return

        last = candles[-1]
        prev = candles[-2]

        # ===============================
        # MVP ZONE: STRUCTURE / RANGE
        # ===============================
        if direction == "LONG":
            price_from = min(prev["low"], last["low"])
            price_to = max(prev["high"], last["high"])
        else:
            price_from = min(prev["high"], last["high"])
            price_to = max(prev["low"], last["low"])

        zone = Zone(
            zone_type=ZoneType.STRUCTURE,
            price_from=price_from,
            price_to=price_to,
        )

        self._zones.append(zone)

        event_bus.publish(
            Event(
                type=EventType.ZONE_CREATED,
                symbol=symbol,
                payload={
                    "zone_type": zone.zone_type.value,
                    "from": zone.price_from,
                    "to": zone.price_to,
                },
            )
        )

    def get_active_zones(self) -> list[Zone]:
        return [
            z for z in self._zones
            if z.status == ZoneStatus.ACTIVE
        ]
