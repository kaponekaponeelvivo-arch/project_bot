from typing import Optional, List

from core.scanner_core.events import Event, EventType
from core.scanner_core.events.event_bus import EventBus
from core.scanner_core.impulse.impulse import Impulse


class ImpulseValidationDetector:
    """
    Confirms impulse quality AFTER IMPULSE_DETECTED.
    Does NOT cancel anything.
    """

    def __init__(self) -> None:
        self._validated: bool = False

    def reset(self) -> None:
        self._validated = False

    def analyze(
        self,
        symbol: str,
        market_data: dict,
        impulse: Optional[Impulse],
        direction: str,
        market_context: str,
        event_bus: EventBus,
    ) -> None:

        if impulse is None or self._validated:
            return

        candles: List[dict] = market_data.get("candles", [])
        if len(candles) < 2:
            return

        last = candles[-1]

        # Контекст должен совпадать
        if direction == "LONG" and market_context != "TREND_UP":
            return
        if direction == "SHORT" and market_context != "TREND_DOWN":
            return

        # 1️⃣ Продолжение движения
        continuation = False
        if direction == "LONG":
            continuation = last["close"] > impulse.end_price
        elif direction == "SHORT":
            continuation = last["close"] < impulse.end_price

        # 2️⃣ Нет полного возврата в тело импульса
        body_low = min(impulse.start_price, impulse.end_price)
        body_high = max(impulse.start_price, impulse.end_price)

        invalid_retrace = body_low <= last["close"] <= body_high

        if continuation and not invalid_retrace:
            self._validated = True
            event_bus.publish(
                Event(
                    type=EventType.IMPULSE_CONFIRMED,
                    symbol=symbol,
                )
            )
