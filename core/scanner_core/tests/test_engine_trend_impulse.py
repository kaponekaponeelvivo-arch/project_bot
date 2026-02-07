from core.scanner_core.engine import ScannerEngine


def print_step(step: int, result: dict) -> None:
    print(f"\n--- STEP {step} ---")
    print(f"Symbol: {result['symbol']}")
    print(f"State: {result['state']}")
    print(f"State changed: {result['state_changed']}")

    if not result["events"]:
        print("Events: none")
        return

    print("Events:")
    for e in result["events"]:
        print(f" - {e.type.value}")


def build_trend_up_candles() -> list[dict]:
    candles = []

    price = 100.0
    for i in range(30):
        open_price = price
        close_price = price + 0.3          # higher close
        high = close_price + 0.2
        low = open_price - 0.1

        candles.append({
            "open": open_price,
            "close": close_price,
            "high": high,
            "low": low,
            "volume": 100 + i,              # stable volume
        })

        price = close_price

    return candles


def build_impulse_candle(last_price: float) -> dict:
    return {
        "open": last_price,
        "close": last_price + 2.0,          # strong bullish candle
        "high": last_price + 2.3,
        "low": last_price - 0.2,
        "volume": 300,                      # volume expansion
    }


if __name__ == "__main__":
    print("=== ENGINE TEST: TREND → IMPULSE ===")

    engine = ScannerEngine()

    # ===============================
    # STEP 1 — Trend context only
    # ===============================
    candles = build_trend_up_candles()

    market_data = {
        "candles": candles
    }

    result = engine.run("SOLUSDT", market_data)
    print_step(1, result)

    # ===============================
    # STEP 2 — Add impulse candle
    # ===============================
    impulse = build_impulse_candle(candles[-1]["close"])
    candles.append(impulse)

    market_data = {
        "candles": candles
    }

    result = engine.run("SOLUSDT", market_data)
    print_step(2, result)

    print("\n=== TEST FINISHED ===")
