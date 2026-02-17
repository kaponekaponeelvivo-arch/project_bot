from enum import Enum


class EventType(Enum):

    # ===============================
    # MARKET CONTEXT
    # ===============================
    MARKET_CONTEXT_CHANGED = "market_context_changed"

    # ===============================
    # STRUCTURAL PHASES
    # ===============================
    IMPULSE_DETECTED = "impulse_detected"
    CORRECTION_STARTED = "correction_started"
    ZONE_REACTED = "zone_reacted"

    SCENARIO_CONFIRMED = "scenario_confirmed"
    SCENARIO_COMPLETED = "scenario_completed"
    SCENARIO_CANCELLED = "scenario_cancelled"

    # ===============================
    # WATCHLIST
    # ===============================
    WATCHLIST_UPDATED = "watchlist_updated"
