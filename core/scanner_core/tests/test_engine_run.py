from core.scanner_core.engine import ScannerEngine
from core.scanner_core.state_machine import ScenarioState


def fake_market_data():
    """
    Минимальные данные-заглушки,
    которые ожидают наши детекторы.
    """
    return {
        "start_price": 100,
        "end_price": 110,
        "zone_from": 105,
        "zone_to": 108,
    }


def run_engine_test():
    engine = ScannerEngine()

    symbol = "SOLUSDT"
    direction = "LONG"

    print("=== ENGINE TEST START ===")

    # Прогон нескольких циклов
    for step in range(1, 4):
        result = engine.run(
            symbol=symbol,
            market_data=fake_market_data(),
            direction=direction,
        )

        print(f"\n--- STEP {step} ---")

        if result is None:
            print("No result returned")
            continue

        print("Symbol:", result.symbol)
        print("State:", result.state.value)
        print("State changed:", result.state_changed)

        if result.events:
            print("Events:")
            for e in result.events:
                print(f" - {e.type.value}")
        else:
            print("Events: none")

        # Проверка, что состояние валидное
        assert isinstance(result.state, ScenarioState)

    print("\n=== ENGINE TEST FINISHED ===")


if __name__ == "__main__":
    run_engine_test()
