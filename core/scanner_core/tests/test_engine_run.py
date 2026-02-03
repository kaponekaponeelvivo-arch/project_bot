# core/scanner_core/tests/test_engine_run.py

from core.scanner_core.engine import ScannerEngine


def print_step(step: int, result: dict):
    print(f"\n--- STEP {step} ---")
    print(f"Symbol: {result['symbol']}")
    print(f"State: {result['state']}")
    print(f"State changed: {result['state_changed']}")

    events = result.get("events", [])
    if not events:
        print("Events: none")
    else:
        print("Events:")
        for e in events:
            # e может быть Event или строка — защищаемся
            if hasattr(e, "type"):
                print(f" - {e.type.value}")
            else:
                print(f" - {e}")


def main():
    print("=== ENGINE TEST START ===")

    engine = ScannerEngine()

    # -------------------------------------------------
    # STEP 1 — просто рынок, без импульса
    # -------------------------------------------------
    market_data_1 = {
        "candles": [
            {"open": 100, "high": 102, "low": 99, "close": 101, "volume": 100},
            {"open": 101, "high": 103, "low": 100, "close": 102, "volume": 110},
            {"open": 102, "high": 104, "low": 101, "close": 103, "volume": 120},
        ]
    }

    result = engine.run("SOLUSDT", market_data_1)
    print_step(1, result)

    # -------------------------------------------------
    # STEP 2 — импульсная свеча
    # -------------------------------------------------
    market_data_2 = {
        "candles": [
            {"open": 100, "high": 102, "low": 99, "close": 101, "volume": 100},
            {"open": 101, "high": 103, "low": 100, "close": 102, "volume": 110},
            {"open": 102, "high": 104, "low": 101, "close": 103, "volume": 120},
            {"open": 103, "high": 110, "low": 102, "close": 109, "volume": 300},
        ]
    }

    result = engine.run("SOLUSDT", market_data_2)
    print_step(2, result)

    # -------------------------------------------------
    # STEP 3 — потеря импульсной структуры (коррекция)
    # -------------------------------------------------
    market_data_3 = {
        "candles": [
            {"open": 103, "high": 110, "low": 102, "close": 109, "volume": 300},
            {"open": 109, "high": 110, "low": 104, "close": 105, "volume": 180},
        ]
    }

    result = engine.run("SOLUSDT", market_data_3)
    print_step(3, result)

    # -------------------------------------------------
    # STEP 4 — касание зоны и реакция
    # -------------------------------------------------
    market_data_4 = {
        "candles": [
            {"open": 105, "high": 106, "low": 103, "close": 104, "volume": 150},
            {"open": 104, "high": 108, "low": 103, "close": 107, "volume": 220},
        ]
    }

    result = engine.run("SOLUSDT", market_data_4)
    print_step(4, result)

    print("\n=== ENGINE TEST FINISHED ===")


if __name__ == "__main__":
    main()
