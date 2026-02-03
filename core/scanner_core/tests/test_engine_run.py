# core/scanner_core/tests/test_engine_run.py

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

    # ==================================================
    # STEP 1 — обычный рынок, без импульса
    # ==================================================
    market_data_1 = {
        "candles": [
            {"open": 100, "high": 101, "low": 99, "close": 100.5, "volume": 100},
            {"open": 100.5, "high": 101.2, "low": 100, "close": 101, "volume": 110},
            {"open": 101, "high": 101.5, "low": 100.8, "close": 101.2, "volume": 105},
            {"open": 101.2, "high": 101.6, "low": 100.9, "close": 101.1, "volume": 102},
            {"open": 101.1, "high": 101.7, "low": 101, "close": 101.3, "volume": 108},
            {"open": 101.3, "high": 101.8, "low": 101.1, "close": 101.4, "volume": 107},
        ]
    }

    result = engine.run("SOLUSDT", market_data_1)
    print_step(1, result)

    # ==================================================
    # STEP 2 — появляется импульс
    # ==================================================
    market_data_2 = {
        "candles": market_data_1["candles"] + [
            {
                "open": 101.4,
                "high": 104.5,
                "low": 101.3,
                "close": 104.2,
                "volume": 220,
            }
        ]
    }

    result = engine.run("SOLUSDT", market_data_2)
    print_step(2, result)

    # ==================================================
    # STEP 3 — FSM должен перейти в IMPULSE
    # ==================================================
    market_data_3 = {
        "candles": market_data_2["candles"] + [
            {
                "open": 104.2,
                "high": 105.0,
                "low": 103.8,
                "close": 104.6,
                "volume": 180,
            }
        ]
    }

    result = engine.run("SOLUSDT", market_data_3)
    print_step(3, result)

    print("\n=== ENGINE TEST FINISHED ===")
