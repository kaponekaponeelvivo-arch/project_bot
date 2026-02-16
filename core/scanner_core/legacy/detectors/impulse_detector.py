from core.scanner_core.events import Event, EventType
from core.scanner_core.market_context.context import ContextValidity


class ImpulseDetector:

    def __init__(self) -> None:
        self._in_impulse = False
        self._direction = None
        self._start_price = None
        self._extreme_price = None
        self._start_index = None

    def analyze(
        self,
        symbol: str,
        market_data: dict,
        direction: str,
        market_context,
        event_bus,
    ) -> None:

        candles = market_data.get("candles", [])
        if len(candles) < 10:
            return

        if not market_context:
            return

        if market_context.validity != ContextValidity.VALID:
            return

        phase = getattr(market_context, "phase", None)
        if not phase:
            return

        if phase.name not in ("TREND_UP", "TREND_DOWN"):
            return

        trend_direction = "LONG" if phase.name == "TREND_UP" else "SHORT"

        if trend_direction != direction:
            return

        last = candles[-1]
        price = last["close"]

        if not self._in_impulse:

            if phase.name == "TREND_UP":
                prev_high = max(c["high"] for c in candles[-5:-1])
                if price <= prev_high:
                    return
                self._extreme_price = last["high"]
            else:
                prev_low = min(c["low"] for c in candles[-5:-1])
                if price >= prev_low:
                    return
                self._extreme_price = last["low"]

            self._in_impulse = True
            self._direction = trend_direction
            self._start_price = price
            self._start_index = len(candles) - 1

            event_bus.publish(
                Event(
                    type=EventType.IMPULSE_DETECTED,
                    symbol=symbol,
                    payload={
                        "start_price": self._start_price,
                        "end_price": self._extreme_price,
                        "move_percent": 0,
                        "duration_candles": 1,
                    },
                )
            )
            return

        if self._direction == "LONG":
            if last["high"] > self._extreme_price:
                self._extreme_price = last["high"]
        else:
            if last["low"] < self._extreme_price:
                self._extreme_price = last["low"]

        move = abs(self._extreme_price - self._start_price)
        if move <= 0:
            return

        move_percent = (move / self._start_price) * 100
        if move_percent < 2:
            return

        retrace = abs(self._extreme_price - price)
        retrace_ratio = retrace / move

        if retrace_ratio >= 0.30:  # 🔥 было 0.45

            duration = len(candles) - self._start_index

            event_bus.publish(
                Event(
                    type=EventType.CORRECTION_STARTED,
                    symbol=symbol,
                    payload={
                        "start_price": self._start_price,
                        "end_price": self._extreme_price,
                        "move_percent": round(move_percent, 2),
                        "duration_candles": duration,
                    },
                )
            )

            self._reset()

    def _reset(self):
        self._in_impulse = False
        self._direction = None
        self._start_price = None
        self._extreme_price = None
        self._start_index = None
