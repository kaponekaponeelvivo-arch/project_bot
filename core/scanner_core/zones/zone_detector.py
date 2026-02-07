from typing import Optional

from core.scanner_core.events import Event, EventType
from core.scanner_core.events.event_bus import EventBus
from core.scanner_core.zones.zone import Zone
from core.scanner_core.zones.zone_types import ZoneType
from core.scanner_core.zones.zone_manager import ZoneManager
from core.scanner_core.state_machine import ScenarioState


class ZoneDetector:
    """
    Detects zones during CORRECTION phase.

    Zones are derived from impulse extremes
    provided via CORRECTION_STARTED event payload.
    """

    def __init__(self) -> None:
        self._last_impulse_high: Optional[float] = None
        self._last_impulse_low: Optional[float] = None

    def analyze(
        self,
        symbol: str,
        market_data: dict,
        scenario,
        zone_manager: ZoneManager,
        event_bus: EventBus,
    ) -> None:

        # Zones are created ONLY once per correction
        if scenario.state != ScenarioState.CORRECTION:
            return

        # Extract impulse data from scenario events
        impulse_event = next(
            (
                e for e in reversed(scenario.events)
                if e.type == EventType.CORRECTION_STARTED
            ),
            None,
        )

        if not impulse_event:
            return

        impulse_high = impulse_event.payload.get("impulse_high")
        impulse_low = impulse_event.payload.get("impulse_low")

        if impulse_high is None or impulse_low is None:
            return

        # Prevent duplicate zone creation
        if self._last_impulse_high == impulse_high and self._last_impulse_low == impulse_low:
            return

        self._last_impulse_high = impulse_high
        self._last_impulse_low = impulse_low

        # ===============================
        # CREATE CONSERVATIVE ZONE
        # ===============================
        price_from = impulse_low + (impulse_high - impulse_low) * 0.5
        price_to = impulse_low + (impulse_high - impulse_low) * 0.618

        zone = Zone(
            symbol=symbol,
            zone_type=ZoneType.STRUCTURE,
            price_from=round(price_from, 4),
            price_to=round(price_to, 4),
        )

        zone_manager.add_zone(
            zone=zone,
            event_bus=event_bus,
            symbol=symbol,
        )
