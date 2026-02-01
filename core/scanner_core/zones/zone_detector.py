from typing import List

from core.scanner_core.events import Event, EventType
from core.scanner_core.events.event_bus import EventBus
from core.scanner_core.zones.zone import Zone
from core.scanner_core.zones.zone_types import ZoneType
from core.scanner_core.zones.zone_status import ZoneStatus
from core.scanner_core.zones.zone_manager import ZoneManager


class ZoneDetector:
    """
    MVP Zone detector.

    Zones are created ONLY on CORRECTION_STARTED.
    Zones are passive context, not signals.
    """

    def analyze(
        self,
        symbol: str,
        market_data: dict,
        zone_manager: ZoneManager,
        event_bus: EventBus,
    ) -> List[Zone]:

        created_zones: List[Zone] = []

        candles = market_data.get("candles", [])
        if not candles:
            return created_zones

        # =========================================
        # 1. MAIN ZONE — IMPULSE RANGE (RANGE)
        # =========================================
        impulse_high = None
        impulse_low = None

        for c in candles:
            high = c.get("high")
            low = c.get("low")

            if impulse_high is None or high > impulse_high:
                impulse_high = high
            if impulse_low is None or low < impulse_low:
                impulse_low = low

        if impulse_high is not None and impulse_low is not None:
            range_zone = Zone(
                zone_type=ZoneType.RANGE,
                price_from=impulse_low,
                price_to=impulse_high,
                status=ZoneStatus.ACTIVE,
            )

            zone_manager.add(range_zone)
            created_zones.append(range_zone)

            event_bus.publish(
                Event(
                    type=EventType.ZONE_CREATED,
                    symbol=symbol,
                    payload={
                        "type": range_zone.zone_type.value,
                        "price_from": range_zone.price_from,
                        "price_to": range_zone.price_to,
                    },
                )
            )

        # =========================================
        # 2. STRUCTURAL ZONE (HL / LH) — MVP
        # =========================================
        if len(candles) >= 3:
            prev = candles[-3]
            mid = candles[-2]

            # simple structural pause
            is_pause = (
                mid["high"] < prev["high"]
                and mid["low"] > prev["low"]
            )

            if is_pause:
                structure_zone = Zone(
                    zone_type=ZoneType.STRUCTURE,
                    price_from=mid["low"],
                    price_to=mid["high"],
                    status=ZoneStatus.ACTIVE,
                )

                zone_manager.add(structure_zone)
                created_zones.append(structure_zone)

                event_bus.publish(
                    Event(
                        type=EventType.ZONE_CREATED,
                        symbol=symbol,
                        payload={
                            "type": structure_zone.zone_type.value,
                            "price_from": structure_zone.price_from,
                            "price_to": structure_zone.price_to,
                        },
                    )
                )

        return created_zones
