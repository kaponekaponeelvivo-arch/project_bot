# core/scanner_core/impulse/impulse_detector.py

from typing import Optional
from datetime import datetime

from core.scanner_core.events import Event, EventType
from core.scanner_core.events.event_bus import EventBus
from .impulse import Impulse


class ImpulseDetector:
    """
    Detects impulse start and impulse exhaustion.
    Impulse is detected once and never recalculated.
    """

    def __init__(self) -> None:
        self._active_impulse: Optional[Impulse] = None

    def analyze(
        self,
        symbol: str,
        market_data: dict,
        direction: str,
        event_bus: EventBus,
    ) -> Optional[Impulse]:
        """
        Analyze market data and publish impulse events.

        market_data — любые подготовленные данные (OHLC, range, etc)
        direction — "LONG" or "SHORT"
        """

        # ===============================
        # TODO: REAL LOGIC WILL BE HERE
        # ===============================
        impulse_detected = False
        impulse_exhausted = False
        # ===============================

        # --- DETECT IMPULSE ---
        if impulse_detected and self._active_impulse is None:
            impulse = Impulse(
                direction=direction,
                start_price=market_data["start_price"],
                end_price=market_data["end_price"],
                started_at=datetime.utcnow(),
                finished_at=datetime.utcnow(),
            )

            self._active_impulse = impulse

            event_bus.publish(
                Event(
                    type=EventType.IMPULSE_DETECTED,
                    symbol=symbol,
                    payload={"direction": direction},
                )
            )

            return impulse

        # --- EXHAUST IMPULSE ---
        if impulse_exhausted and self._active_impulse is not None:
            event_bus.publish(
                Event(
                    type=EventType.IMPULSE_EXHAUSTED,
                    symbol=symbol,
                )
            )

            self._active_impulse = None

        return self._active_impulse
