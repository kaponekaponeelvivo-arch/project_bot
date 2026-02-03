from typing import List

from core.scanner_core.events import Event, EventType
from core.scanner_core.events.event_bus import EventBus


class ConfirmedDetector:
    """
    Detects CONFIRMED state.
    Confirmation happens AFTER reaction,
    when price shows valid continuation from zone.
    """

    def analyze(
        self,
        symbol: str,
        market_data: dict,
        direction: str,
        event_bus: EventBus,
    ) -> None:

        candles: List[dict] = market_data.get("candles", [])
        if len(candles) < 3:
            return

        last = candles[-1]
        prev = candles[-2]

        # ===============================
        # 1️⃣ Local structure break
        # ===============================
        structure_break = False

        if direction == "LONG":
            structure_break = last["close"] > prev["high"]
        elif direction == "SHORT":
            structure_break = last["close"] < prev["low"]

        # ===============================
        # 2️⃣ Impulse candle confirmation
        # ===============================
        body = abs(last["close"] - last["open"])
        full = last["high"] - last["low"]

        if full == 0:
            return

        body_ratio = body / full

        impulse_candle = body_ratio >= 0.6

        direction_ok = (
            direction == "LONG" and last["close"] > last["open"]
        ) or (
            direction == "SHORT" and last["close"] < last["open"]
        )

        # ===============================
        # 3️⃣ Final CONFIRMED decision
        # ===============================
        if direction_ok and (structure_break or impulse_candle):
            event_bus.publish(
                Event(
                    type=EventType.SCENARIO_CONFIRMED,
                    symbol=symbol,
                )
            )
