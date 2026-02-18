from typing import List, Dict, Optional


class StructureBuilder:
    """
    Pivot-based structural impulse builder (HH/HL model).
    Работает только с 1H свечами.
    """

    LOOKBACK_CANDLES = 300
    PIVOT_PERIOD = 5
    MIN_IMPULSE_PERCENT = 25
    MIN_IMPULSE_CANDLES = 15

    # ==========================================================
    # PUBLIC
    # ==========================================================

    def find_long_impulse(self, candles: List[Dict]) -> Optional[Dict]:
        candles = candles[-self.LOOKBACK_CANDLES:]

        pivots_low = self._find_pivot_lows(candles)
        pivots_high = self._find_pivot_highs(candles)

        if not pivots_low or not pivots_high:
            return None

        last_low_index = pivots_low[-1]

        # Ищем первый HH после последнего swing low
        valid_highs = [i for i in pivots_high if i > last_low_index]

        if not valid_highs:
            return None

        last_high_index = valid_highs[-1]

        if last_high_index - last_low_index < self.MIN_IMPULSE_CANDLES:
            return None

        start_price = candles[last_low_index]["low"]
        end_price = candles[last_high_index]["high"]

        move_percent = ((end_price - start_price) / start_price) * 100

        if move_percent < self.MIN_IMPULSE_PERCENT:
            return None

        return {
            "start_index": last_low_index,
            "end_index": last_high_index,
            "impulse_low": start_price,
            "impulse_high": end_price,
            "start_price": start_price,
            "end_price": end_price,
            "move_percent": move_percent,
        }

    # ==========================================================

    def find_short_impulse(self, candles: List[Dict]) -> Optional[Dict]:
        candles = candles[-self.LOOKBACK_CANDLES:]

        pivots_high = self._find_pivot_highs(candles)
        pivots_low = self._find_pivot_lows(candles)

        if not pivots_high or not pivots_low:
            return None

        last_high_index = pivots_high[-1]

        valid_lows = [i for i in pivots_low if i > last_high_index]

        if not valid_lows:
            return None

        last_low_index = valid_lows[-1]

        if last_low_index - last_high_index < self.MIN_IMPULSE_CANDLES:
            return None

        start_price = candles[last_high_index]["high"]
        end_price = candles[last_low_index]["low"]

        move_percent = ((start_price - end_price) / start_price) * 100

        if move_percent < self.MIN_IMPULSE_PERCENT:
            return None

        return {
            "start_index": last_high_index,
            "end_index": last_low_index,
            "impulse_high": start_price,
            "impulse_low": end_price,
            "start_price": start_price,
            "end_price": end_price,
            "move_percent": move_percent,
        }

    # ==========================================================
    # INTERNAL
    # ==========================================================

    def _find_pivot_lows(self, candles: List[Dict]) -> List[int]:
        pivots = []
        p = self.PIVOT_PERIOD

        for i in range(p, len(candles) - p):
            current_low = candles[i]["low"]

            left = candles[i - p : i]
            right = candles[i + 1 : i + 1 + p]

            if all(current_low < c["low"] for c in left) and \
               all(current_low < c["low"] for c in right):
                pivots.append(i)

        return pivots

    # ==========================================================

    def _find_pivot_highs(self, candles: List[Dict]) -> List[int]:
        pivots = []
        p = self.PIVOT_PERIOD

        for i in range(p, len(candles) - p):
            current_high = candles[i]["high"]

            left = candles[i - p : i]
            right = candles[i + 1 : i + 1 + p]

            if all(current_high > c["high"] for c in left) and \
               all(current_high > c["high"] for c in right):
                pivots.append(i)

        return pivots
