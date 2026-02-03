from typing import List

from core.scanner_core.events import Event, EventType
from core.scanner_core.events.event_bus import EventBus
from core.scanner_core.zones.zone import Zone


class ReactionDetector:
    """
    Detects price reaction from active zones.
    Reaction != confirmation.
    """

    def analyze(
        self,
        symbol: str,
        market_data: dict,
        zone: Zone,
        direction: str,
        event_bus: EventBus,
    ) -> None:

        candles: List[dict] = market_data.get("candles", [])
        if len(candles) < 2:
            return

        last = candles[-1]

        # ===============================
        # 1️⃣ Price touched zone
        # ===============================
        touched = (
            last["low"] <= zone.price_to
            and last["high"] >= zone.price_from
        )

        if not touched:
            return

        # ===============================
        # 2️⃣ Candle characteristics
        # ===============================
        body = abs(last["close"] - last["open"])
        full = last["high"] - last["low"]

        if full == 0:
            return

        body_ratio = body / full

        bullish = last["close"] > last["open"]
        bearish = last["close"] < last["open"]

        direction_ok = (
            direction == "LONG" and bullish
        ) or (
            direction == "SHORT" and bearish
        )

        impulse_candle = body_ratio >= 0.6

        # ===============================
        # 3️⃣ Wick-based reaction
        # ===============================
        upper_wick = last["high"] - max(last["open"], last["close"])
        lower_wick = min(last["open"], last["close"]) - last["low"]

        wick_reaction = False
        if direction == "LONG" and lower_wick > body:
            wick_reaction = True
        if direction == "SHORT" and upper_wick > body:
            wick_reaction = True

        # ===============================
        # 4️⃣ Final decision
        # ===============================
        if direction_ok and (impulse_candle or wick_reaction):
            event_bus.publish(
                Event(
                    type=EventType.ZONE_REACTED,
                    symbol=symbol,
                    payload={
                        "zone_id": zone.id,
                        "zone_type": zone.zone_type.value,
                    },
                )
            )

