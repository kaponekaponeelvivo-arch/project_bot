from core.scanner_core.events import Event, EventType
from core.scanner_core.events.event_bus import EventBus

from .zone import Zone
from .zone_types import ZoneType
from .zone_status import ZoneStatus
from .zone_manager import ZoneManager


class ZoneDetector:
    """
    Detects zones and their interaction with price.
    Produces ONLY facts → events.
    """

    def analyze(
        self,
        symbol: str,
        market_data: dict,
        zone_manager: ZoneManager,
        event_bus: EventBus,
    ) -> None:
        """
        market_data — prepared data (candles, ranges, etc.)
        """

        # ===============================
        # PLACEHOLDER FOR REAL LOGIC
        # ===============================
        zone_created = False
        zone_touched = False
        zone_reacted = False
        zone_invalidated = False
        # ===============================

        # --- CREATE ZONE ---
        if zone_created:
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
                    },
                )
            )

        # --- UPDATE EXISTING ZONES ---
        for zone in zone_manager.active():

            if zone_touched:
                zone.set_status(ZoneStatus.TOUCHED)
                event_bus.publish(
                    Event(
                        type=EventType.ZONE_TOUCHED,
                        symbol=symbol,
                        payload={"zone_id": zone.id},
                    )
                )

            if zone_reacted:
                zone.set_status(ZoneStatus.REACTED)
                event_bus.publish(
                    Event(
                        type=EventType.ZONE_REACTED,
                        symbol=symbol,
                        payload={"zone_id": zone.id},
                    )
                )

            if zone_invalidated:
                zone.set_status(ZoneStatus.INVALIDATED)
                event_bus.publish(
                    Event(
                        type=EventType.ZONE_INVALIDATED,
                        symbol=symbol,
                        payload={"zone_id": zone.id},
                    )
                )
