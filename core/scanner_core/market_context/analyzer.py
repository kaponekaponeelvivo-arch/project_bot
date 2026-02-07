from typing import Optional, List

from core.scanner_core.events import Event, EventType
from core.scanner_core.events.event_bus import EventBus
from .context import MarketContext, MarketPhase, ContextValidity


class MarketContextAnalyzer:
    """
    SMART Market Context Analyzer.

    Window: last 30 candles
    Purpose:
    - determine market phase (TREND_UP / TREND_DOWN / RANGE)
    - determine context validity (VALID / INVALID)
    - protect FSM from noise and chaos
    """

    WINDOW = 30
    MIN_STRUCTURE_POINTS = 3  # HH/HL or LL/LH confirmations

    def __init__(self) -> None:
        self._last_context: Optional[MarketContext] = None

    def analyze(self, market_data: dict, event_bus: EventBus) -> MarketContext:
        candles: List[dict] = market_data.get("candles", [])

        # ===============================
        # 0️⃣ Safety: insufficient data
        # ===============================
        if len(candles) < self.WINDOW:
            context = MarketContext(
                phase=MarketPhase.RANGE,
                validity=ContextValidity.VALID,
            )
            self._last_context = context
            return context

        window = candles[-self.WINDOW:]

        highs = [c["high"] for c in window]
        lows = [c["low"] for c in window]
        closes = [c["close"] for c in window]

        max_high = max(highs)
        min_low = min(lows)
        range_size = max_high - min_low

        # Hard safety
        if range_size == 0:
            context = MarketContext(
                phase=MarketPhase.RANGE,
                validity=ContextValidity.INVALID,
            )
            self._emit_if_changed(context, event_bus)
            self._last_context = context
            return context

        # ===============================
        # 1️⃣ STRUCTURE ANALYSIS
        # ===============================
        higher_highs = 0
        higher_lows = 0
        lower_lows = 0
        lower_highs = 0

        for i in range(1, len(window)):
            if highs[i] > highs[i - 1]:
                higher_highs += 1
            if lows[i] > lows[i - 1]:
                higher_lows += 1
            if lows[i] < lows[i - 1]:
                lower_lows += 1
            if highs[i] < highs[i - 1]:
                lower_highs += 1

        # ===============================
        # 2️⃣ PRICE LOCATION
        # ===============================
        last_close = closes[-1]
        position_in_range = (last_close - min_low) / range_size

        # ===============================
        # 3️⃣ PHASE DECISION
        # ===============================
        phase = MarketPhase.RANGE

        if (
            higher_highs >= self.MIN_STRUCTURE_POINTS
            and higher_lows >= self.MIN_STRUCTURE_POINTS
            and position_in_range > 0.55
        ):
            phase = MarketPhase.TREND_UP

        elif (
            lower_lows >= self.MIN_STRUCTURE_POINTS
            and lower_highs >= self.MIN_STRUCTURE_POINTS
            and position_in_range < 0.45
        ):
            phase = MarketPhase.TREND_DOWN

        # ===============================
        # 4️⃣ VALIDITY CHECK
        # ===============================
        validity = ContextValidity.VALID

        # Chaos filter: extreme candles
        extreme_bodies = 0
        for c in window[-5:]:
            body = abs(c["close"] - c["open"])
            full = c["high"] - c["low"]
            if full > 0 and body / full > 0.85:
                extreme_bodies += 1

        if extreme_bodies >= 3:
            validity = ContextValidity.INVALID

        # Trend contradiction protection
        if phase == MarketPhase.TREND_UP and position_in_range < 0.3:
            validity = ContextValidity.INVALID

        if phase == MarketPhase.TREND_DOWN and position_in_range > 0.7:
            validity = ContextValidity.INVALID

        context = MarketContext(
            phase=phase,
            validity=validity,
        )

        self._emit_if_changed(context, event_bus)
        self._last_context = context
        return context

    # ===============================
    # INTERNAL
    # ===============================
    def _emit_if_changed(self, new: MarketContext, event_bus: EventBus) -> None:
        if self._last_context is None:
            return

        if new.phase != self._last_context.phase:
            event_bus.publish(
                Event(
                    type=EventType.MARKET_CONTEXT_CHANGED,
                    symbol="MARKET",
                    payload={
                        "from": self._last_context.phase.value,
                        "to": new.phase.value,
                    },
                )
            )

        if new.validity != self._last_context.validity:
            event_bus.publish(
                Event(
                    type=EventType.CONTEXT_INVALIDATED,
                    symbol="MARKET",
                )
            )
