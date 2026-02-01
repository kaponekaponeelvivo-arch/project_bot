from enum import Enum


class EventType(Enum):
    # ===============================
    # MARKET / CONTEXT
    # ===============================
    MARKET_CONTEXT_CHANGED = "market_context_changed"
    MARKET_PHASE_CHANGED = "market_phase_changed"
    CONTEXT_INVALIDATED = "context_invalidated"

    # ===============================
    # TREND / STRUCTURE
    # ===============================
    TREND_DETECTED = "trend_detected"
    STRUCTURE_BROKEN = "structure_broken"

    # ===============================
    # IMPULSE
    # ===============================
    IMPULSE_DETECTED = "impulse_detected"
    IMPULSE_EXHAUSTED = "impulse_exhausted"

    # ===============================
    # CORRECTION / RANGE
    # ===============================
    CORRECTION_STARTED = "correction_started"
    CORRECTION_INVALID = "correction_invalid"
    RANGE_FORMED = "range_formed"
    RANGE_BROKEN = "range_broken"

    # ===============================
    # ZONES
    # ===============================
    ZONE_CREATED = "zone_created"
    ZONE_TOUCHED = "zone_touched"
    ZONE_REACTED = "zone_reacted"
    ZONE_INVALIDATED = "zone_invalidated"

    # ===============================
    # REACTION
    # ===============================
    REACTION_DETECTED = "reaction_detected"

    # ===============================
    # SCENARIO LIFECYCLE
    # ===============================
    SCENARIO_STARTED = "scenario_started"
    SCENARIO_CONFIRMED = "scenario_confirmed"
    SCENARIO_COMPLETED = "scenario_completed"
    SCENARIO_CANCELLED = "scenario_cancelled"
