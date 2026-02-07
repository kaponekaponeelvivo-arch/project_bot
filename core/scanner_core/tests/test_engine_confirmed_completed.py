from core.scanner_core.engine import ScannerEngine
from core.scanner_core.state_machine import ScenarioState


def print_step(step: int, result: dict):
    print(f"\n--- STEP {step} ---")
    print(f"Symbol: {result['symbol']}")
    print(f"State: {result['state']}")
    print(f"State changed: {result['state_changed']}")
    if result["events"]:
        print("Events:")
        for e in result["events"]:
            print(f" - {e.type.value}")
    else:
        print("Events: none")


print("=== ENGINE TEST: CONFIRMED → COMPLETED ===")

engine = ScannerEngine()
symbol = "SOLUSDT"

# --------------------------------
# STEP 1 — вручную ставим CONFIRMED
# --------------------------------
scenario = engine._scenario_manager.create(
    symbol=symbol,
    direction="LONG",
)
scenario.set_state(ScenarioState.CONFIRMED)

# стартуем tracking
engine._tracking.start(symbol, confirm_price=100)

# --------------------------------
# STEP 2 — движение +4%
# --------------------------------
market_data = {
    "candles": [
        {
            "open": 100,
            "high": 105,
            "low": 99,
            "close": 104,  # +4%
            "volume": 2000,
        }
    ]
}

# первый прогон — публикуется событие
result = engine.run(symbol, market_data)
print_step(1, result)

# второй прогон — FSM применяет COMPLETED
result = engine.run(symbol, market_data)
print_step(2, result)

print("\n=== TEST FINISHED ===")
