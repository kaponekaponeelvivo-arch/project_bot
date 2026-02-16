from typing import Dict, List
from core.scanner_core.events import Event, EventType
from core.scanner_core.market_context.context import (
    MarketContext,
    MarketPhase,
    ContextValidity,
)


class MarketContextAnalyzer:
    """
    4H Swing Structure Trend Model

    TREND_UP if:
        - 2 Higher High
        - 2 Higher Low
        - Range between swing low/high >= 12%

    TREND_DOWN if:
        - 2 Lower Low
        - 2 Lower High
        - Range >= 12%

    Otherwise RANGE.
    """

    MIN_RANGE_PERCENT = 12  # 🔥 было 17
    SWING_LOOKBACK = 2

    def __init__(self) -> None:
        self._last_context: MarketContext | None = None

    def analyze(self, market_data: Dict, event_bus) -> MarketContext:

        candles: List[dict] = market_data.get("candles", [])

        if len(candles) < 20:
            context = MarketContext(
                phase=MarketPhase.RANGE,
                validity=ContextValidity.INVALID,
            )
            self._last_context = context
            return context

        swing_highs, swing_lows = self._find_swings(candles)
        phase = self._determine_phase(swing_highs, swing_lows)

        context = MarketContext(
            phase=phase,
            validity=ContextValidity.VALID,
        )

        if self._last_context is not None:
            if context.phase != self._last_context.phase:
                event_bus.publish(
                    Event(
                        type=EventType.MARKET_CONTEXT_CHANGED,
                        symbol="GLOBAL",
                        payload={"phase": context.phase.name},
                    )
                )

        self._last_context = context
        return context

    def _find_swings(self, candles: List[dict]):
        highs = []
        lows = []

        for i in range(self.SWING_LOOKBACK, len(candles) - self.SWING_LOOKBACK):
            current = candles[i]

            left = candles[i - self.SWING_LOOKBACK : i]
            right = candles[i + 1 : i + 1 + self.SWING_LOOKBACK]

            if all(current["high"] > c["high"] for c in left + right):
                highs.append((i, current["high"]))

            if all(current["low"] < c["low"] for c in left + right):
                lows.append((i, current["low"]))

        return highs, lows

    def _determine_phase(self, swing_highs, swing_lows):

        if len(swing_highs) < 2 or len(swing_lows) < 2:
            return MarketPhase.RANGE

        last_high_1 = swing_highs[-1][1]
        last_high_2 = swing_highs[-2][1]

        last_low_1 = swing_lows[-1][1]
        last_low_2 = swing_lows[-2][1]

        is_higher_high = last_high_1 > last_high_2
        is_higher_low = last_low_1 > last_low_2

        is_lower_high = last_high_1 < last_high_2
        is_lower_low = last_low_1 < last_low_2

        range_percent = abs(last_high_1 - last_low_1) / last_low_1 * 100

        if range_percent < self.MIN_RANGE_PERCENT:
            return MarketPhase.RANGE

        if is_higher_high and is_higher_low:
            return MarketPhase.TREND_UP

        if is_lower_high and is_lower_low:
            return MarketPhase.TREND_DOWN

        return MarketPhase.RANGE
