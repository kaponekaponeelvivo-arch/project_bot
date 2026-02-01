from typing import List, Optional

from .zone import Zone
from .zone_status import ZoneStatus


class ZoneManager:
    """
    Stores and manages zones inside ONE scenario.
    """

    def __init__(self) -> None:
        self._zones: List[Zone] = []

    def add(self, zone: Zone) -> None:
        self._zones.append(zone)

    def all(self) -> List[Zone]:
        return self._zones

    def active(self) -> List[Zone]:
        return [z for z in self._zones if z.status == ZoneStatus.ACTIVE]

    def get(self, zone_id: str) -> Optional[Zone]:
        for zone in self._zones:
            if zone.id == zone_id:
                return zone
        return None

    def invalidate(self, zone_id: str) -> None:
        zone = self.get(zone_id)
        if zone:
            zone.set_status(ZoneStatus.INVALIDATED)
