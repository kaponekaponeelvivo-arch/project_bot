import time
from typing import List

from core.scanner_core.engine import ScannerEngine
from core.scanner_core.live.bybit_client import BybitClient


class BybitRunner:
    """
    Live market runner (multi-TF)

    5M  -> Entry / Confirmation TF
    15M -> Reaction TF
    1H  -> Impulse / Correction TF
    4H  -> Global trend TF
    """

    def __init__(
        self,
        symbols: List[str],
        limit: int = 200,
        loop_delay: int = 60,
    ) -> None:
        self.symbols = symbols
        self.limit = limit
        self.loop_delay = loop_delay

        self._client = BybitClient()
        self._engine = ScannerEngine()

    def run(self) -> None:
        print("=" * 50)
        print("[BYBIT] Live runner started")
        print(f"[BYBIT] Symbols loaded: {len(self.symbols)}")
        print("[BYBIT] TF: 5M | 15M | 1H | 4H")
        print("=" * 50)

        while True:
            for symbol in self.symbols:
                try:
                    print(f"[BYBIT] Fetching candles: {symbol}")

                    # ===============================
                    # 5M – Entry / Confirmation
                    # ===============================
                    working_data = self._client.get_candles(
                        symbol=symbol,
                        interval="5",
                        limit=self.limit,
                    )

                    if not working_data or not working_data.get("candles"):
                        print(f"[BYBIT][WARN] No 5M candles for {symbol}")
                        continue

                    # ===============================
                    # 15M – Reaction TF
                    # ===============================
                    reaction_data = self._client.get_candles(
                        symbol=symbol,
                        interval="15",
                        limit=self.limit,
                    )

                    if not reaction_data or not reaction_data.get("candles"):
                        print(f"[BYBIT][WARN] No 15M candles for {symbol}")
                        continue

                    # ===============================
                    # 1H – Impulse / Correction
                    # ===============================
                    impulse_data = self._client.get_candles(
                        symbol=symbol,
                        interval="60",
                        limit=self.limit,
                    )

                    if not impulse_data or not impulse_data.get("candles"):
                        print(f"[BYBIT][WARN] No 1H candles for {symbol}")
                        continue

                    # ===============================
                    # 4H – Global Trend
                    # ===============================
                    context_data = self._client.get_candles(
                        symbol=symbol,
                        interval="240",
                        limit=self.limit,
                    )

                    if not context_data or not context_data.get("candles"):
                        print(f"[BYBIT][WARN] No 4H candles for {symbol}")
                        continue

                    self._engine.run(
                        symbol=symbol,
                        market_data=working_data,      # 5M
                        reaction_data=reaction_data,  # 15M
                        impulse_data=impulse_data,    # 1H
                        context_data=context_data,    # 4H
                    )

                except Exception as e:
                    print(f"[BYBIT][ERROR] {symbol}: {e}")

            time.sleep(self.loop_delay)


# ==================================================
# ENTRYPOINT
# ==================================================
if __name__ == "__main__":

    client = BybitClient()
    symbols = client.get_top_symbols(limit=100)

    runner = BybitRunner(
        symbols=symbols,
        limit=200,
        loop_delay=60,
    )

    runner.run()
