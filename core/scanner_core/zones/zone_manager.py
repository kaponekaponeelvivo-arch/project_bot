from collections import defaultdict
from typing import Dict, List

from .zone import Zone
from .zone_status import ZoneStatus


class ZoneManager:
    """
    Stores and manages zones per symbol.
    """

    def __init__(self) -> None:
        self._zones: Dict[str, List[Zone]] = defaultdict(list)

    def add(self, symbol: str, zone: Zone) -> None:
        self._zones[symbol].append(zone)

    def get_active_zones(self, symbol: str) -> List[Zone]:
        """
        Return active zones for given symbol.
        """
        return [
            z for z in self._zones.get(symbol, [])
            if z.status == ZoneStatus.ACTIVE
        ]

    def invalidate_zone(self, symbol: str, zone: Zone) -> None:
        """
        Mark zone as invalidated.
        """
        zone.set_status(ZoneStatus.INVALIDATED)

    def react_zone(self, symbol: str, zone: Zone) -> None:
        """
        Mark zone as reacted.
        """
        zone.set_status(ZoneStatus.REACTED)
