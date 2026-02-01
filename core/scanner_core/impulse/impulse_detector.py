from typing import Optional, List
from datetime import datetime

from core.scanner_core.events import Event, EventType
from core.scanner_core.events.event_bus import EventBus
from .impulse import Impulse


class ImpulseDetector:
    """
    Real impulse detector (MVP).

    Rules:
    - Impulse ONLY by trend
    - Directional range expansion
    - Relative volume expansion
    """

    def __init__(self) -> None:
        self._active_impulse: Optional[Impulse] = None

    def analyze(
        self,
        symbol: str,
        market_data: dict,
        direction: str,
        market_context,
        event_bus: EventBus,
    ) -> Optional[Impulse]:
        """
        market_context — value returned by MarketContextAnalyzer
        market_data expected format:
        {
            "candles": [
                {"open": float, "high": float, "low": float, "close": float, "volume": float},
                ...
            ]
        }
        """

        # ===============================
        # 1. PRECONDITION: TREND ONLY
        # ===============================
        if market_context not in ("TREND_UP", "TREND_DOWN"):
            return self._active_impulse

        candles: List[dict] = market_data.get("candles", [])
        if len(candles) < 6:
            return self._active_impulse

        recent = candles[-1]
        window = candles[-6:-1]

        # ===============================
        # 2. RANGE EXPANSION
        # ===============================
        recent_range = recent["high"] - recent["low"]
        avg_range = sum(c["high"] - c["low"] for c in window) / len(window)

        range_expansion = recent_range > avg_range

        # ===============================
        # 3. DIRECTION CHECK
        # ===============================
        bullish = recent["close"] > recent["open"]
        bearish = recent["close"] < recent["open"]

        direction_ok = (
            market_context == "TREND_UP" and bullish
        ) or (
            market_context == "TREND_DOWN" and bearish
        )

        # ===============================
        # 4. RELATIVE VOLUME CONFIRMATION
        # ===============================
        recent_volume = recent["volume"]
        avg_volume = sum(c["volume"] for c in window) / len(window)

        volume_ok = recent_volume > avg_volume

        # ===============================
        # 5. FINAL IMPULSE CONDITION
        # ===============================
        impulse_detected = (
            range_expansion
            and direction_ok
            and volume_ok
            and self._active_impulse is None
        )

        if not impulse_detected:
            return self._active_impulse

        # ===============================
        # 6. CREATE IMPULSE + EVENT
        # ===============================
        impulse = Impulse(
            direction=direction,
            start_price=window[0]["open"],
            end_price=recent["close"],
            started_at=datetime.utcnow(),
            finished_at=datetime.utcnow(),
        )

        self._active_impulse = impulse

        event_bus.publish(
            Event(
                type=EventType.IMPULSE_DETECTED,
                symbol=symbol,
                payload={
                    "direction": direction,
                    "range_expansion": True,
                    "volume_confirmed": True,
                },
            )
        )

        return impulse
