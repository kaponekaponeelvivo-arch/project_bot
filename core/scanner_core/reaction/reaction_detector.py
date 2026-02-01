from typing import Dict

from core.scanner_core.events.event import Event
from core.scanner_core.events.event_types import EventType
from core.scanner_core.zones.zone import Zone
from core.scanner_core.zones.zone_status import ZoneStatus


class ReactionDetector:
    """
    Detects reaction from zone and decides whether scenario is CONFIRMED.

    IMPORTANT:
    - Reaction ≠ Impulse
    - Impulse-like movement from zone is treated as CONFIRMED, not new impulse
    """

    def analyze(
        self,
        symbol: str,
        market_data: Dict,
        zone: Zone,
        direction: str,
        event_bus,
    ) -> None:

        # ===============================
        # 0. Preconditions
        # ===============================
        if zone.status != ZoneStatus.ACTIVE:
            return

        # Price may have different keys depending on data source
        price = (
            market_data.get("price")
            or market_data.get("close")
            or market_data.get("last_price")
        )

        if price is None:
            return

        # price must interact with zone
        if not (zone.price_from <= price <= zone.price_to):
            return

        # ===============================
        # 1. ZONE TOUCHED
        # ===============================
        event_bus.publish(
            Event(
                type=EventType.ZONE_TOUCHED,
                symbol=symbol,
                payload={
                    "zone_id": zone.id,
                    "zone_type": zone.zone_type.value,
                },
            )
        )

        # ===============================
        # 2. CONFIRMED CONDITIONS
        # ===============================

        # --- A. STRUCTURE (MANDATORY) ---
        structure_confirmed = market_data.get("structure_confirmed", False)
        if not structure_confirmed:
            return

        # --- B. IMPULSE-LIKE REACTION ---
        impulse_strength = market_data.get("impulse_strength", 0.0)
        impulse_confirmed = impulse_strength >= 1.0

        # --- C. VOLUME (OPTIONAL) ---
        volume_ratio = market_data.get("volume_ratio", 1.0)
        volume_confirmed = volume_ratio >= 1.2

        # Require: A + (B or C)
        if not (impulse_confirmed or volume_confirmed):
            return

        # ===============================
        # 3. CONFIRMED
        # ===============================
        zone.set_status(ZoneStatus.REACTED)

        event_bus.publish(
            Event(
                type=EventType.SCENARIO_CONFIRMED,
                symbol=symbol,
                payload={
                    "zone_id": zone.id,
                    "direction": direction,
                    "structure": True,
                    "impulse": impulse_confirmed,
                    "volume": volume_confirmed,
                },
            )
        )
