from typing import Optional

from .context import MarketContext, MarketPhase, ContextValidity
from core.scanner_core.events.event_bus import EventBus


class MarketContextAnalyzer:
    """
    Determines market context (phase + validity).

    MVP-версия:
    - Контекст используется ТОЛЬКО как справочная информация
    - Никакие события (MARKET_PHASE_CHANGED и т.д.) НЕ публикуются
    - Это осознанно, чтобы не шуметь и не ломать FSM
    """

    def __init__(self) -> None:
        self._last_context: Optional[MarketContext] = None

    def analyze(self, market_data: dict, event_bus: EventBus) -> MarketContext:
        """
        Analyze market data and return current market context.

        Пока что:
        - всегда считаем, что рынок в тренде
        - валидный контекст
        """

        # TODO: здесь позже появится реальная логика определения тренда / боковика
        context = MarketContext(
            phase=MarketPhase.TREND_UP,
            validity=ContextValidity.VALID,
        )

        self._last_context = context
        return context
