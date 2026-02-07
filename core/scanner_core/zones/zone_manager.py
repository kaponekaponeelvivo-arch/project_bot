from typing import List, Dict

from core.scanner_core.zones.zone import Zone
from core.scanner_core.zones.zone_status import ZoneStatus
from core.scanner_core.events import Event, EventType
from core.scanner_core.events.event_bus import EventBus


class ZoneManager:
    """
    Manages zones lifecycle and statuses.

    Zone lifecycle:
    ACTIVE -> TOUCHED -> REACTED -> INVALIDATED
    """

    def __init__(self) -> None:
        self._zones: Dict[str, Zone] = {}

    # ===============================
    # REGISTRATION
    # ===============================
    def add_zone(self, zone: Zone, event_bus: EventBus, symbol: str) -> None:
        self._zones[zone.id] = zone

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

    # ===============================
    # STATUS TRANSITIONS
    # ===============================
    def mark_touched(self, zone_id: str, event_bus: EventBus, symbol: str) -> None:
        zone = self._zones.get(zone_id)
        if not zone or zone.status != ZoneStatus.ACTIVE:
            return

        zone.set_status(ZoneStatus.TOUCHED)

        event_bus.publish(
            Event(
                type=EventType.ZONE_TOUCHED,
                symbol=symbol,
                payload={"zone_id": zone.id},
            )
        )

    def mark_reacted(self, zone_id: str, event_bus: EventBus, symbol: str) -> None:
        zone = self._zones.get(zone_id)
        if not zone or zone.status == ZoneStatus.INVALIDATED:
            return

        zone.set_status(ZoneStatus.REACTED)

        event_bus.publish(
            Event(
                type=EventType.ZONE_REACTED,
                symbol=symbol,
                payload={"zone_id": zone.id},
            )
        )

    def invalidate(self, zone_id: str, event_bus: EventBus, symbol: str) -> None:
        zone = self._zones.get(zone_id)
        if not zone or zone.status == ZoneStatus.INVALIDATED:
            return

        zone.set_status(ZoneStatus.INVALIDATED)

        event_bus.publish(
            Event(
                type=EventType.ZONE_INVALIDATED,
                symbol=symbol,
                payload={"zone_id": zone.id},
            )
        )

    # ===============================
    # QUERIES
    # ===============================
    def get_active_zones(self) -> List[Zone]:
        return [
            z for z in self._zones.values()
            if z.status in (ZoneStatus.ACTIVE, ZoneStatus.TOUCHED)
        ]

    def all_zones(self) -> List[Zone]:
        return list(self._zones.values())

    def clear(self) -> None:
        self._zones.clear()

    # ===============================
    # SNAPSHOT (🔥 ВАЖНО ДЛЯ NOTIFICATIONS)
    # ===============================
    def snapshot(self) -> List[dict]:
        return [
            {
                "id": z.id,
                "type": z.zone_type.value,
                "status": z.status.value,
                "price_from": z.price_from,
                "price_to": z.price_to,
            }
            for z in self._zones.values()
        ]
