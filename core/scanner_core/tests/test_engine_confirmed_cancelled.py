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


print("=== ENGINE TEST: CONFIRMED → CANCELLED ===")

engine = ScannerEngine()
symbol = "SOLUSDT"

# --------------------------------
# STEP 0 — создаём CONFIRMED
# --------------------------------
scenario = engine._scenario_manager.create(
    symbol=symbol,
    direction="LONG",
)
scenario.set_state(ScenarioState.CONFIRMED)

engine._tracking.start(symbol, confirm_price=100)

# --------------------------------
# STEP 1 — рынок идёт против
# --------------------------------
market_data = {
    "candles": [
        {
            "open": 100,
            "high": 101,
            "low": 96,
            "close": 97,   # -3%
            "volume": 2500,
        }
    ]
}

result = engine.run(symbol, market_data)
print_step(1, result)

# --------------------------------
# STEP 2 — событие применено FSM
# --------------------------------
result = engine.run(symbol, market_data)
print_step(2, result)
# STEP 3 — применение FSM
result = engine.run(symbol, market_data)
print_step(3, result)

print("\n=== TEST FINISHED ===")
