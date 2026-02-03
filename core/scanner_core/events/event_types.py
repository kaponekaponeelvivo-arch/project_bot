from enum import Enum


class EventType(Enum):
    # ===============================
    # MARKET CONTEXT
    # ===============================
    MARKET_CONTEXT_CHANGED = "market_context_changed"
    CONTEXT_INVALIDATED = "context_invalidated"

    # ===============================
    # SCENARIO LIFECYCLE
    # ===============================
    SCENARIO_STARTED = "scenario_started"
    SCENARIO_CONFIRMED = "scenario_confirmed"
    SCENARIO_COMPLETED = "scenario_completed"
    SCENARIO_CANCELLED = "scenario_cancelled"

    # ===============================
    # IMPULSE
    # ===============================
    IMPULSE_DETECTED = "impulse_detected"
    IMPULSE_EXHAUSTED = "impulse_exhausted"

    # ===============================
    # CORRECTION
    # ===============================
    CORRECTION_STARTED = "correction_started"

    # ===============================
    # ZONES
    # ===============================
    ZONE_CREATED = "zone_created"
    ZONE_REACTED = "zone_reacted"
    ZONE_INVALIDATED = "zone_invalidated"

    # ===============================
    # STRUCTURE
    # ===============================
    STRUCTURE_BROKEN = "structure_broken"
