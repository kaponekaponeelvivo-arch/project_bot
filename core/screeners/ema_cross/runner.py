from typing import Iterable, List

from core.screeners.ema_cross.detector import EmaCrossDetector
from core.screeners.ema_cross.models import EmaCrossEvent, Timeframe
from core.services.notification_gate import NotificationGate
from core.services.market_filter import MarketFilterService


class EmaCrossRunner:
    """
    Orchestrates EMA Cross scanning:
    Market Filter → EMA Core → Notification Gate
    """

    def __init__(
        self,
        user_id: int,
        market_filter_service: MarketFilterService,
        notification_gate: NotificationGate,
    ):
        self.user_id = user_id
        self.market_filter_service = market_filter_service
        self.notification_gate = notification_gate

    async def run(
        self,
        timeframe: Timeframe,
        mode: str,
        ema_fast_prev: float,
        ema_slow_prev: float,
        ema_fast_now: float,
        ema_slow_now: float,
        distance_extreme_threshold: float,
    ) -> List[EmaCrossEvent]:
        """
        Runs EMA Cross for all allowed symbols.
        Returns list of events that passed NotificationGate.
        """

        events: List[EmaCrossEvent] = []

        symbols: Iterable[str] = await self.market_filter_service.get_symbols(
            user_id=self.user_id
        )

        for symbol in symbols:
            detector = EmaCrossDetector(
                symbol=symbol,
                timeframe=timeframe,
                mode=mode,
                distance_extreme_threshold=distance_extreme_threshold,
            )

            event = detector.detect(
                ema_fast_prev=ema_fast_prev,
                ema_slow_prev=ema_slow_prev,
                ema_fast_now=ema_fast_now,
                ema_slow_now=ema_slow_now,
            )

            if event is None:
                continue

            allowed = await self.notification_gate.can_send(
                telegram_id=self.user_id
            )

            if not allowed:
                continue

            await self.notification_gate.register_send(
                telegram_id=self.user_id
            )

            events.append(event)

        return events
