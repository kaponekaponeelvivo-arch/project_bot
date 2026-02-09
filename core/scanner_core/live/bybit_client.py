import requests
from typing import Dict, List


class BybitClient:
    """
    Public READ-ONLY Bybit client.
    Uses v5 Market API.
    """

    BASE_URL = "https://api.bybit.com"

    def get_candles(
        self,
        symbol: str,
        interval: str,
        limit: int = 200,
    ) -> Dict[str, List[dict]]:
        """
        Fetch kline data from Bybit.

        interval:
        1  = 1m
        3  = 3m
        5  = 5m
        15 = 15m
        60 = 1h
        """

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

        # Bybit returns newest → oldest, we reverse
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
