import requests
from typing import Dict, List


class BybitClient:
    """
    Public READ-ONLY Bybit client.
    Uses v5 Market API.
    """

    BASE_URL = "https://api.bybit.com"

    # ==================================================
    # CANDLES
    # ==================================================
    def get_candles(
        self,
        symbol: str,
        interval: str,
        limit: int = 200,
    ) -> Dict[str, List[dict]]:

        url = f"{self.BASE_URL}/v5/market/kline"

        params = {
            "category": "linear",
            "symbol": symbol,
            "interval": interval,
            "limit": limit,
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        if data.get("retCode") != 0:
            raise RuntimeError(
                f"Bybit API error {data.get('retCode')}: {data.get('retMsg')}"
            )

        raw = data["result"]["list"]

        candles = []
        for c in reversed(raw):
            candles.append(
                {
                    "open_time": int(c[0]),
                    "open": float(c[1]),
                    "high": float(c[2]),
                    "low": float(c[3]),
                    "close": float(c[4]),
                    "volume": float(c[5]),
                }
            )

        return {"candles": candles}

    # ==================================================
    # TOP SYMBOLS BY 24H VOLUME
    # ==================================================
    def get_top_symbols(self, limit: int = 100) -> List[str]:
        """
        Returns top USDT perpetual symbols sorted by 24h turnover.
        """

        url = f"{self.BASE_URL}/v5/market/tickers"

        params = {
            "category": "linear",
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        if data.get("retCode") != 0:
            raise RuntimeError(
                f"Bybit API error {data.get('retCode')}: {data.get('retMsg')}"
            )

        tickers = data["result"]["list"]

        # Filter only USDT perpetual
        usdt_pairs = [
            t for t in tickers
            if t["symbol"].endswith("USDT")
        ]

        # Sort by 24h turnover
        sorted_pairs = sorted(
            usdt_pairs,
            key=lambda x: float(x.get("turnover24h", 0)),
            reverse=True,
        )

        top_symbols = [t["symbol"] for t in sorted_pairs[:limit]]

        return top_symbols
