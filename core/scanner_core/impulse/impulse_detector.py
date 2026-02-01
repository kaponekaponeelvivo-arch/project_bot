from typing import Optional, List
from datetime import datetime

from core.scanner_core.events import Event, EventType
from core.scanner_core.events.event_bus import EventBus
from .impulse import Impulse


class ImpulseDetector:
    """
    Impulse + Correction detector (MVP).

    Responsibilities:
    - Detect impulse by trend, range, volume
    - Track active impulse
    - Detect loss of impulse structure -> CORRECTION_STARTED
    """

    def __init__(self) -> None:
        self._active_impulse: Optional[Impulse] = None
        self._impulse_high: Optional[float] = None
        self._impulse_low: Optional[float] = None

    def analyze(
        self,
        symbol: str,
        market_data: dict,
        direction: str,
        market_context,
        event_bus: EventBus,
    ) -> Optional[Impulse]:

        candles: List[dict] = market_data.get("candles", [])
        if len(candles) < 6:
            return self._active_impulse

        recent = candles[-1]
        window = candles[-6:-1]

        # ==================================================
        # 1. DETECT IMPULSE (ONLY IF NONE ACTIVE)
        # ==================================================
        if self._active_impulse is None:

            if market_context not in ("TREND_UP", "TREND_DOWN"):
                return None

            recent_range = recent["high"] - recent["low"]
            avg_range = sum(c["high"] - c["low"] for c in window) / len(window)

            range_expansion = recent_range > avg_range

            bullish = recent["close"] > recent["open"]
            bearish = recent["close"] < recent["open"]

            direction_ok = (
                market_context == "TREND_UP" and bullish
            ) or (
                market_context == "TREND_DOWN" and bearish
            )

            recent_volume = recent["volume"]
            avg_volume = sum(c["volume"] for c in window) / len(window)

            volume_ok = recent_volume > avg_volume

            impulse_detected = range_expansion and direction_ok and volume_ok

            if not impulse_detected:
                return None

            impulse = Impulse(
                direction=direction,
                start_price=window[0]["open"],
                end_price=recent["close"],
                started_at=datetime.utcnow(),
                finished_at=datetime.utcnow(),
            )

            self._active_impulse = impulse
            self._impulse_high = recent["high"]
            self._impulse_low = recent["low"]

            event_bus.publish(
                Event(
                    type=EventType.IMPULSE_DETECTED,
                    symbol=symbol,
                )
            )

            return impulse

        # ==================================================
        # 2. TRACK IMPULSE STRUCTURE
        # ==================================================
        self._impulse_high = max(self._impulse_high, recent["high"])
        self._impulse_low = min(self._impulse_low, recent["low"])

        # ==================================================
        # 3. DETECT LOSS OF IMPULSE STRUCTURE (CORRECTION)
        # ==================================================
        correction_started = False

        # A) no continuation
        if (
            market_context == "TREND_UP"
            and recent["close"] < self._impulse_high
        ):
            correction_started = True

        if (
            market_context == "TREND_DOWN"
            and recent["close"] > self._impulse_low
        ):
            correction_started = True

        # B) deep opposite close (inside impulse body)
        impulse_body_mid = (
            self._impulse_high + self._impulse_low
        ) / 2

        if market_context == "TREND_UP" and recent["close"] < impulse_body_mid:
            correction_started = True

        if market_context == "TREND_DOWN" and recent["close"] > impulse_body_mid:
            correction_started = True

        if not correction_started:
            return self._active_impulse

        # ==================================================
        # 4. START CORRECTION
        # ==================================================
        event_bus.publish(
            Event(
                type=EventType.CORRECTION_STARTED,
                symbol=symbol,
                payload={
                    "impulse_high": self._impulse_high,
                    "impulse_low": self._impulse_low,
                },
            )
        )

        self._active_impulse = None
        self._impulse_high = None
        self._impulse_low = None

        return None
