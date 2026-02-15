import time
from typing import List

from core.scanner_core.engine import ScannerEngine
from core.scanner_core.live.bybit_client import BybitClient


class BybitRunner:
    """
    Live market runner for Bybit (READ-ONLY).

    - Fetches candles from Bybit
    - Feeds them into ScannerEngine
    - Prints basic activity to terminal (UX)
    """

    def __init__(
        self,
        symbols: List[str],
        interval: str = "1",   # 1m candles (test mode)
        limit: int = 200,      # enough for context + impulse
        loop_delay: int = 60,  # seconds
    ) -> None:
        self.symbols = symbols
        self.interval = interval
        self.limit = limit
        self.loop_delay = loop_delay

        self._client = BybitClient()
        self._engine = ScannerEngine()

    def run(self) -> None:
        print("=" * 50)
        print("[BYBIT] Live runner started")
        print(f"[BYBIT] Symbols: {len(self.symbols)}")
        print(f"[BYBIT] Timeframe: {self.interval}m | Limit: {self.limit}")
        print("=" * 50)

        while True:
            for symbol in self.symbols:
                try:
                    print(f"[BYBIT] Fetching candles: {symbol}")

                    market_data = self._client.get_candles(
                        symbol=symbol,
                        interval=self.interval,
                        limit=self.limit,
                    )

                    if not market_data or not market_data.get("candles"):
                        print(f"[BYBIT][WARN] No candles for {symbol}")
                        continue

                    self._engine.run(symbol, market_data)

                except Exception as e:
                    print(f"[BYBIT][ERROR] {symbol}: {e}")

            time.sleep(self.loop_delay)


# ==================================================
# ENTRYPOINT
# ==================================================
if __name__ == "__main__":

    # 🔹 Expanded liquid symbols (Bybit USDT Perpetuals)
    SYMBOLS = [
        "BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT",
        "ADAUSDT", "AVAXUSDT", "DOGEUSDT", "DOTUSDT", "LINKUSDT",
        "MATICUSDT", "TONUSDT", "LTCUSDT", "BCHUSDT", "TRXUSDT",
        "OPUSDT", "ARBUSDT", "APTUSDT", "NEARUSDT", "ATOMUSDT",
        "UNIUSDT", "SUIUSDT", "SEIUSDT", "TIAUSDT", "INJUSDT",
        "FILUSDT", "AAVEUSDT", "FTMUSDT", "ALGOUSDT", "XLMUSDT",
        "ETCUSDT", "MKRUSDT", "EGLDUSDT", "THETAUSDT", "RUNEUSDT",
        "GRTUSDT", "IMXUSDT", "PEPEUSDT", "WIFUSDT", "BONKUSDT",
        "JUPUSDT", "PYTHUSDT", "ENAUSDT", "RNDRUSDT", "LDOUSDT",
        "EOSUSDT", "STXUSDT", "ICPUSDT", "HBARUSDT", "FLOWUSDT",
        "VETUSDT", "SANDUSDT", "MANAUSDT", "AXSUSDT", "CHZUSDT",
        "KASUSDT", "GMTUSDT", "DYDXUSDT", "CRVUSDT", "1INCHUSDT",
        "COMPUSDT", "SNXUSDT", "YFIUSDT", "KAVAUSDT", "ZILUSDT",
        "ROSEUSDT", "CELOUSDT", "BLURUSDT", "PENDLEUSDT", "ORDIUSDT",
        "BOMEUSDT", "NOTUSDT", "WLDUSDT", "TAOUSDT", "ONDOUSDT",
        "JASMYUSDT", "FETUSDT", "AGIXUSDT", "OCEANUSDT", "ANKRUSDT",
        "CFXUSDT", "QNTUSDT", "BATUSDT", "ZRXUSDT", "NKNUSDT",
        "SFPUSDT", "RAYUSDT", "TRBUSDT", "ENSUSDT", "MASKUSDT",
        "API3USDT", "GMXUSDT", "ARUSDT", "MEMEUSDT", "NEOUSDT",
    ]

    runner = BybitRunner(
        symbols=SYMBOLS,
        interval="1",     # 1m = ускоренное тестирование
        limit=200,
        loop_delay=60,    # обновление раз в минуту
    )

    runner.run()
