from core.scanner_core.events import Event, EventType
from core.scanner_core.events.event_bus import EventBus

from .zone import Zone
from .zone_types import ZoneType
from .zone_manager import ZoneManager


class ZoneDetector:
    """
    Zone detector.
    TEMPORARY test logic:
    - creates ONE zone immediately on CORRECTION
    """

    def __init__(self) -> None:
        self._zone_created: bool = False

    def analyze(
        self,
        symbol: str,
        market_data: dict,
        zone_manager: ZoneManager,
        event_bus: EventBus,
    ) -> None:
        """
        market_data — prepared data (stub for now)
        """

        # ===============================
        # TEMP TEST LOGIC (CONTROLLED)
        # ===============================
        zone_should_be_created = not self._zone_created
        # ===============================

        if zone_should_be_created:
            self._zone_created = True

            zone = Zone(
                zone_type=ZoneType.IMBALANCE,
                price_from=market_data["zone_from"],
                price_to=market_data["zone_to"],
            )
            zone_manager.add(zone)

            event_bus.publish(
                Event(
                    type=EventType.ZONE_CREATED,
                    symbol=symbol,
                    payload={
                        "zone_id": zone.id,
                        "zone_type": zone.zone_type.value,
                        "price_from": zone.price_from,
                        "price_to": zone.price_to,
                    },
                )
            )
