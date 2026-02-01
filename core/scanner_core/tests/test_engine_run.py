from core.scanner_core.engine import ScannerEngine
from core.scanner_core.market_context.analyzer import MarketContextAnalyzer

print("=== ENGINE TEST START ===")

# --------------------------------
# STUB MARKET CONTEXT
# --------------------------------
def fake_analyze(self, market_data, event_bus):
    return "TREND_UP"

MarketContextAnalyzer.analyze = fake_analyze

# --------------------------------
# ENGINE
# --------------------------------
engine = ScannerEngine()

# --------------------------------
# TEST MARKET DATA (VALID IMPULSE)
# --------------------------------
market_data = {
    "candles": [
        {"open": 100, "high": 102, "low": 99, "close": 101, "volume": 100},
        {"open": 101, "high": 103, "low": 100, "close": 102, "volume": 110},
        {"open": 102, "high": 104, "low": 101, "close": 103, "volume": 105},
        {"open": 103, "high": 105, "low": 102, "close": 104, "volume": 115},
        {"open": 104, "high": 106, "low": 103, "close": 105, "volume": 120},
        {"open": 105, "high": 112, "low": 104, "close": 111, "volume": 300},
    ]
}

# --------------------------------
# STEP 1
# --------------------------------
result = engine.run(
    symbol="SOLUSDT",
    market_data=market_data,
    direction="LONG",
)

print("\n--- STEP 1 ---")
print(f"Symbol: {result.symbol}")
print(f"State: {result.state.value}")
print(f"State changed: {result.state_changed}")

if result.events:
    print("Events:")
    for e in result.events:
        print(f" - {e.type.value}")
else:
    print("Events: none")

# --------------------------------
# STEP 2 (NO REPEAT)
# --------------------------------
result = engine.run(
    symbol="SOLUSDT",
    market_data=market_data,
    direction="LONG",
)

print("\n--- STEP 2 ---")
print(f"Symbol: {result.symbol}")
print(f"State: {result.state.value}")
print(f"State changed: {result.state_changed}")

if result.events:
    print("Events:")
    for e in result.events:
        print(f" - {e.type.value}")
else:
    print("Events: none")

print("\n=== ENGINE TEST FINISHED ===")
# --------------------------------
# STEP 3 (zones should appear here)
# --------------------------------
result = engine.run(
    symbol="SOLUSDT",
    market_data=market_data,
    direction="LONG",
)

print("\n--- STEP 3 ---")
print(f"Symbol: {result.symbol}")
print(f"State: {result.state.value}")
print(f"State changed: {result.state_changed}")

if result.events:
    print("Events:")
    for e in result.events:
        print(f" - {e.type.value}")
else:
    print("Events: none")
