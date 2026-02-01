from core.scanner_core.engine import ScannerEngine


def print_step(step, result):
    print(f"\n--- STEP {step} ---")
    print(f"Symbol: {result.symbol}")
    print(f"State: {result.state.value}")
    print(f"State changed: {result.state_changed}")

    if result.events:
        print("Events:")
        for event in result.events:
            print(f" - {event.type.value}")
    else:
        print("Events: none")


if __name__ == "__main__":
    print("=== ENGINE TEST START ===")

    engine = ScannerEngine()

    # STEP 1 — impulse
    market_data_1 = {
        "price": 100,
        "structure_confirmed": True,
        "impulse_strength": 1.5,
        "volume_ratio": 1.3,
        "trend": "up",
    }

    result = engine.run(
        symbol="SOLUSDT",
        market_data=market_data_1,
    )
    print_step(1, result)

    # STEP 2 — correction
    market_data_2 = {
        "price": 98,
        "structure_confirmed": False,
        "impulse_strength": 0.4,
        "volume_ratio": 0.8,
        "trend": "up",
    }

    result = engine.run(
        symbol="SOLUSDT",
        market_data=market_data_2,
    )
    print_step(2, result)

    # STEP 3 — reaction + tracking
    market_data_3 = {
        "price": 103,
        "structure_confirmed": True,
        "impulse_strength": 1.4,
        "volume_ratio": 1.2,
        "trend": "up",
    }

    result = engine.run(
        symbol="SOLUSDT",
        market_data=market_data_3,
    )
    print_step(3, result)

    print("\n=== ENGINE TEST FINISHED ===")
