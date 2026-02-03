from core.scanner_core.engine import ScannerEngine


def print_step(step: int, result: dict) -> None:
    print(f"\n--- STEP {step} ---")
    print(f"Symbol: {result['symbol']}")
    print(f"State: {result['state']}")
    print(f"State changed: {result['state_changed']}")

    if result["events"]:
        print("Events:")
        for e in result["events"]:
            print(f" - {e}")
    else:
        print("Events: none")


if __name__ == "__main__":
    print("=== ENGINE TEST START ===")

    engine = ScannerEngine()

    market_data_1 = {
        "candles": [
            {"open": 100, "high": 102, "low": 99, "close": 101, "volume": 100},
            {"open": 101, "high": 103, "low": 100, "close": 102, "volume": 120},
            {"open": 102, "high": 105, "low": 101, "close": 104, "volume": 200},
            {"open": 104, "high": 108, "low": 103, "close": 107, "volume": 300},
            {"open": 107, "high": 110, "low": 106, "close": 109, "volume": 400},
            {"open": 109, "high": 115, "low": 108, "close": 114, "volume": 600},
        ]
    }

    market_data_2 = {
        "candles": market_data_1["candles"] + [
            {"open": 114, "high": 115, "low": 108, "close": 109, "volume": 250},
            {"open": 109, "high": 110, "low": 104, "close": 105, "volume": 220},
        ]
    }

    market_data_3 = {
        "candles": market_data_2["candles"] + [
            {"open": 105, "high": 108, "low": 104, "close": 107, "volume": 260},
        ]
    }

    result = engine.run("SOLUSDT", market_data_1)
    print_step(1, result)

    result = engine.run("SOLUSDT", market_data_2)
    print_step(2, result)

    result = engine.run("SOLUSDT", market_data_3)
    print_step(3, result)

    print("\n=== ENGINE TEST FINISHED ===")
