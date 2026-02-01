# core/scanner_core/market_context/analyzer.py
from typing import Optional

from .context import MarketContext, MarketPhase, ContextValidity
from core.scanner_core.events import Event, EventType
from core.scanner_core.events.event_bus import EventBus


class MarketContextAnalyzer:
    """
    Determines market phase and validity.
    Generates context-related events.
    """

    def __init__(self) -> None:
        self._last_context: Optional[MarketContext] = None

    def analyze(self, market_data: dict, event_bus: EventBus) -> MarketContext:
        """
        Analyze market data and publish context events if needed.
        """

        # TODO: replace with real structure logic
        new_context = MarketContext(
            phase=MarketPhase.RANGE,
            validity=ContextValidity.VALID,
        )

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

        # Validity changed
        if new_context.validity != self._last_context.validity:
            event_bus.publish(
                Event(
                    type=EventType.CONTEXT_INVALIDATED
                    if new_context.validity == ContextValidity.INVALID
                    else EventType.CONTEXT_RESTORED,
                    symbol="MARKET",
                )
            )

        self._last_context = new_context
        return new_context
