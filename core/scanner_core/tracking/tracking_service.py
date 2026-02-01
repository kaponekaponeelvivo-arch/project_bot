from typing import Dict

from core.scanner_core.events.event import Event
from core.scanner_core.events.event_types import EventType


PROGRESS_STEP_PERCENT = 3.0


class TrackingService:
    """
    Handles post-CONFIRMED tracking:
    - progress notifications every +3%
    - no influence on state machine
    - no TP logic (TP is market-driven)
    """

    def __init__(self) -> None:
        self._last_reported_step: Dict[str, float] = {}

    def track(
        self,
        symbol: str,
        market_data: Dict,
        confirmed_price: float,
        direction: str,
        event_bus,
    ) -> None:

        # -------------------------------
        # Resolve price safely
        # -------------------------------
        price = (
            market_data.get("price")
            or market_data.get("close")
            or market_data.get("last_price")
        )

        if price is None:
            return

        # -------------------------------
        # Calculate movement %
        # -------------------------------
        if direction == "long":
            movement_pct = ((price - confirmed_price) / confirmed_price) * 100
        else:
            movement_pct = ((confirmed_price - price) / confirmed_price) * 100

        if movement_pct < PROGRESS_STEP_PERCENT:
            return

        # -------------------------------
        # Determine current step
        # -------------------------------
        current_step = (
            int(movement_pct // PROGRESS_STEP_PERCENT) * PROGRESS_STEP_PERCENT
        )

        last_step = self._last_reported_step.get(symbol, 0.0)

        if current_step <= last_step:
            return

        # -------------------------------
        # Publish progress update
        # -------------------------------
        self._last_reported_step[symbol] = current_step

        event_bus.publish(
            Event(
                type=EventType.PROGRESS_UPDATE,
                symbol=symbol,
                payload={
                    "progress_percent": current_step,
                    "direction": direction,
                },
            )
        )
