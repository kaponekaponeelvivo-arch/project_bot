import time
from typing import List

from core.scanner_core.engine import ScannerEngine
from core.scanner_core.live.bybit_client import BybitClient


class BybitRunner:
    """
    Live market runner (multi-TF)

    5M  -> Working TF
    1H  -> Impulse TF
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
        print("[BYBIT] TF: 5M | 1H | 4H")
        print("=" * 50)

        while True:
            for symbol in self.symbols:
                try:
                    print(f"[BYBIT] Fetching candles: {symbol}")

                    # 5M working TF
                    working_data = self._client.get_candles(
                        symbol=symbol,
                        interval="5",
                        limit=self.limit,
                    )

                    if not working_data or not working_data.get("candles"):
                        print(f"[BYBIT][WARN] No 5M candles for {symbol}")
                        continue

                    # 1H impulse TF
                    impulse_data = self._client.get_candles(
                        symbol=symbol,
                        interval="60",
                        limit=self.limit,
                    )

                    if not impulse_data or not impulse_data.get("candles"):
                        print(f"[BYBIT][WARN] No 1H candles for {symbol}")
                        continue

                    # 4H context TF
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
                        market_data=working_data,
                        impulse_data=impulse_data,
                        context_data=context_data,
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
