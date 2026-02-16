from enum import Enum


class EventType(Enum):

    # ===============================
    # MARKET CONTEXT
    # ===============================
    MARKET_CONTEXT_CHANGED = "market_context_changed"
    CONTEXT_INVALIDATED = "context_invalidated"

    # ===============================
    # STRUCTURAL PHASES
    # ===============================
    IMPULSE_DETECTED = "impulse_detected"
    CORRECTION_STARTED = "correction_started"

    # ===============================
    # ZONE / REACTION
    # ===============================
    ZONE_REACTED = "zone_reacted"

    # ===============================
    # SCENARIO LIFECYCLE
    # ===============================
    SCENARIO_CONFIRMED = "scenario_confirmed"
    SCENARIO_CANCELLED = "scenario_cancelled"
    SCENARIO_COMPLETED = "scenario_completed"   # 🔥 добавлено

    # ===============================
    # WATCHLIST
    # ===============================
    WATCHLIST_UPDATED = "watchlist_updated"
