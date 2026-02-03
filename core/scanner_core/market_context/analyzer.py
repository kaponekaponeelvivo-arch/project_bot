from typing import Optional, List

from .context import MarketContext, MarketPhase, ContextValidity
from core.scanner_core.events import Event, EventType
from core.scanner_core.events.event_bus import EventBus


class MarketContextAnalyzer:
    """
    Determines market phase (TREND_UP / TREND_DOWN / RANGE)
    using simple structure logic (MVP).
    """

    def __init__(self) -> None:
        self._last_context: Optional[MarketContext] = None

    def analyze(self, market_data: dict, event_bus: EventBus) -> MarketContext:
        candles: List[dict] = market_data.get("candles", [])

        # Not enough data → RANGE
        if len(candles) < 5:
            new_context = MarketContext(
                phase=MarketPhase.RANGE,
                validity=ContextValidity.VALID,
            )
            self._last_context = new_context
            return new_context

        window = candles[-5:]

        highs = [c["high"] for c in window]
        lows = [c["low"] for c in window]

        higher_highs = all(highs[i] > highs[i - 1] for i in range(1, len(highs)))
        higher_lows = all(lows[i] > lows[i - 1] for i in range(1, len(lows)))

        lower_highs = all(highs[i] < highs[i - 1] for i in range(1, len(highs)))
        lower_lows = all(lows[i] < lows[i - 1] for i in range(1, len(lows)))

        if higher_highs and higher_lows:
            phase = MarketPhase.TREND_UP
        elif lower_highs and lower_lows:
            phase = MarketPhase.TREND_DOWN
        else:
            phase = MarketPhase.RANGE

        new_context = MarketContext(
            phase=phase,
            validity=ContextValidity.VALID,
        )

        # First context
        if self._last_context is None:
            self._last_context = new_context
            return new_context

        # Phase changed
        if new_context.phase != self._last_context.phase:
            event_bus.publish(
                Event(
                    type=EventType.MARKET_PHASE_CHANGED,
                    symbol="MARKET",
                    payload={
                        "from": self._last_context.phase.value,
                        "to": new_context.phase.value,
                    },
                )
            )

        self._last_context = new_context
        return new_context
