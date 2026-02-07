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


print("=== ENGINE TEST: REACTION → CONFIRMED ===")

engine = ScannerEngine()
symbol = "SOLUSDT"

# -----------------------------------
# STEP 1 — создаём сценарий в REACTION
# -----------------------------------
scenario = engine._scenario_manager.create(
    symbol=symbol,
    direction="LONG",
)
scenario.set_state(ScenarioState.REACTION)

# -----------------------------------
# STEP 2 — добавляем REACTED-зону
# -----------------------------------
zone = Zone(
    id="zone_1",
    zone_type=ZoneType.IMBALANCE,
    price_from=100,
    price_to=105,
)
zone.set_status(zone.status.REACTED)
engine._zone_manager._zones[zone.id] = zone

# -----------------------------------
# STEP 3 — формируем TREND_UP (30 свечей)
# -----------------------------------
candles = []

price = 80
for _ in range(30):
    candles.append({
        "open": price,
        "high": price + 2,
        "low": price - 1,
        "close": price + 1,
        "volume": 1000,
    })
    price += 1

# -----------------------------------
# STEP 4 — свеча со сломом структуры
# close > previous high
# -----------------------------------
candles.append({
    "open": price,
    "high": price + 5,
    "low": price,
    "close": price + 5,
    "volume": 3000,
})

market_data = {"candles": candles}

result = engine.run(symbol, market_data)
print_step(1, result)

print("\n=== TEST FINISHED ===")
