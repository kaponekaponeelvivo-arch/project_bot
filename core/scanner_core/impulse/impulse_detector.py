from typing import Optional, List
from datetime import datetime

from core.scanner_core.events import Event, EventType
from core.scanner_core.events.event_bus import EventBus
from core.scanner_core.market_context.context import (
    MarketContext,
    MarketPhase,
    ContextValidity,
)
from .impulse import Impulse


class ImpulseDetector:
    """
    Detects impulse and loss of impulse structure.
    """

    def __init__(self) -> None:
        self._active_impulse: Optional[Impulse] = None
        self._impulse_high: Optional[float] = None
        self._impulse_low: Optional[float] = None
        self._no_continuation_count: int = 0
        self._impulse_start_index: Optional[int] = None

    def analyze(
        self,
        symbol: str,
        market_data: dict,
        direction: str,
        market_context: MarketContext,
        event_bus: EventBus,
    ) -> Optional[Impulse]:

        candles: List[dict] = market_data.get("candles", [])
        if len(candles) < 6:
            return self._active_impulse

        # ===============================
        # CONTEXT GUARD
        # ===============================
        if (
            market_context.validity != ContextValidity.VALID
            or market_context.phase
            not in (MarketPhase.TREND_UP, MarketPhase.TREND_DOWN)
        ):
            return self._active_impulse

        recent = candles[-1]
        prev = candles[-2]
        window = candles[-6:-1]

        # ===============================
        # 1️⃣ DETECT IMPULSE
        # ===============================
        if self._active_impulse is None:

            recent_range = recent["high"] - recent["low"]
            avg_range = sum(c["high"] - c["low"] for c in window) / len(window)

            range_expansion = recent_range > avg_range

            bullish = recent["close"] > recent["open"]
            bearish = recent["close"] < recent["open"]

            direction_ok = (
                market_context.phase == MarketPhase.TREND_UP and bullish
            ) or (
                market_context.phase == MarketPhase.TREND_DOWN and bearish
            )

            if not (direction_ok and range_expansion):
                return None

            start_price = window[0]["open"]
            end_price = recent["close"]

            move_pct = round(
                ((end_price - start_price) / start_price) * 100, 2
            )

            impulse = Impulse(
                direction=direction,
                start_price=start_price,
                end_price=end_price,
                started_at=datetime.utcnow(),
                finished_at=datetime.utcnow(),
            )

            self._active_impulse = impulse
            self._impulse_high = recent["high"]
            self._impulse_low = recent["low"]
            self._no_continuation_count = 0
            self._impulse_start_index = len(candles) - 6

            event_bus.publish(
                Event(
                    type=EventType.IMPULSE_DETECTED,
                    symbol=symbol,
                    payload={
                        "start_price": round(start_price, 4),
                        "end_price": round(end_price, 4),
                        "move_percent": move_pct,
                        "duration_candles": 6,
                    },
                )
            )

            return impulse

        # ===============================
        # 2️⃣ TRACK EXTREMES
        # ===============================
        new_high = recent["high"] > self._impulse_high
        new_low = recent["low"] < self._impulse_low

        self._impulse_high = max(self._impulse_high, recent["high"])
        self._impulse_low = min(self._impulse_low, recent["low"])

        if not new_high and not new_low:
            self._no_continuation_count += 1
        else:
            self._no_continuation_count = 0

        # ===============================
        # 3️⃣ LOSS OF IMPULSE
        # ===============================
        correction = False

        if self._no_continuation_count >= 2:
            correction = True

        body_mid = (self._impulse_high + self._impulse_low) / 2

        if (
            market_context.phase == MarketPhase.TREND_UP
            and recent["close"] < body_mid
        ):
            correction = True

        if (
            market_context.phase == MarketPhase.TREND_DOWN
            and recent["close"] > body_mid
        ):
            correction = True

        if (
            market_context.phase == MarketPhase.TREND_UP
            and recent["close"] < prev["low"]
        ):
            correction = True

        if (
            market_context.phase == MarketPhase.TREND_DOWN
            and recent["close"] > prev["high"]
        ):
            correction = True

        if not correction:
            return self._active_impulse

        # ===============================
        # 4️⃣ START CORRECTION
        # ===============================
        impulse_len = (
            len(candles) - self._impulse_start_index
            if self._impulse_start_index is not None
            else None
        )

        event_bus.publish(
            Event(
                type=EventType.CORRECTION_STARTED,
                symbol=symbol,
                payload={
                    "impulse_high": round(self._impulse_high, 4),
                    "impulse_low": round(self._impulse_low, 4),
                    "impulse_duration_candles": impulse_len,
                },
            )
        )

        self._active_impulse = None
        self._impulse_high = None
        self._impulse_low = None
        self._no_continuation_count = 0
        self._impulse_start_index = None

        return None
