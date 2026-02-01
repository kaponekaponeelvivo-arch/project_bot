from typing import List

from core.scanner_core.zones.zone import Zone
from core.scanner_core.zones.zone_status import ZoneStatus


class ZoneManager:
    """
    Stores and manages zones for a single symbol.
    """

    def __init__(self) -> None:
        self._zones: List[Zone] = []

    def add(self, zone: Zone) -> None:
        self._zones.append(zone)

    def get_all(self) -> List[Zone]:
        return list(self._zones)

    def get_active_zones(self) -> List[Zone]:
        """
        Zones that are still valid and can produce reaction.
        """
        return [
            zone for zone in self._zones
            if zone.status == ZoneStatus.ACTIVE
        ]

    def get_reacted_zones(self) -> List[Zone]:
        return [
            zone for zone in self._zones
            if zone.status == ZoneStatus.REACTED
        ]

    def invalidate_all(self) -> None:
        for zone in self._zones:
            zone.set_status(ZoneStatus.INVALIDATED)
