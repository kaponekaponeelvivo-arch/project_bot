from core.scanner_core.engine import ScannerEngine
from core.scanner_core.state_machine import ScenarioState
from core.scanner_core.zones.zone import Zone
from core.scanner_core.zones.zone_types import ZoneType


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


print("=== ENGINE TEST: ZONE → REACTION ===")

engine = ScannerEngine()
symbol = "SOLUSDT"

# --------------------------------
# STEP 1 — сценарий в CORRECTION
# --------------------------------
scenario = engine._scenario_manager.create(
    symbol=symbol,
    direction="LONG",
)
scenario.set_state(ScenarioState.CORRECTION)

# --------------------------------
# STEP 2 — создаём зону
# --------------------------------
zone = Zone(
    id="zone_1",
    zone_type=ZoneType.IMBALANCE,
    price_from=100,
    price_to=105,
)

engine._zone_manager.add_zone(
    zone=zone,
    event_bus=engine._event_bus,
    symbol=symbol,
)

# --------------------------------
# STEP 3 — подход к зоне
# --------------------------------
market_data_1 = {
    "candles": [
        {
            "open": 108,
            "high": 109,
            "low": 106,
            "close": 107,
            "volume": 1500,
        },
        {
            "open": 107,
            "high": 108,
            "low": 104,   # касаемся зоны
            "close": 105,
            "volume": 1800,
        },
    ]
}

result = engine.run(symbol, market_data_1)
print_step(1, result)

# --------------------------------
# STEP 4 — реакция из зоны
# --------------------------------
market_data_2 = {
    "candles": [
        {
            "open": 107,
            "high": 108,
            "low": 104,
            "close": 105,
            "volume": 1800,
        },
        {
            "open": 105,
            "high": 110,
            "low": 104,
            "close": 109,  # импульс из зоны
            "volume": 3000,
        },
    ]
}

result = engine.run(symbol, market_data_2)
print_step(2, result)

print("\n=== TEST FINISHED ===")
