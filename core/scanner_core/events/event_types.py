from enum import Enum


class EventType(Enum):
    # ===============================
    # MARKET CONTEXT
    # ===============================
    MARKET_CONTEXT_CHANGED = "market_context_changed"
    CONTEXT_INVALIDATED = "context_invalidated"

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
    ZONE_TOUCHED = "zone_touched"
    ZONE_REACTED = "zone_reacted"
    ZONE_INVALIDATED = "zone_invalidated"

    # ===============================
    # REACTION / CONFIRMATION
    # ===============================
    REACTION_DETECTED = "reaction_detected"
    SCENARIO_CONFIRMED = "scenario_confirmed"

    # ===============================
    # TRACKING
    # ===============================
    TRACKING_PROGRESS = "tracking_progress"

    # ===============================
    # SCENARIO LIFECYCLE
    # ===============================
    SCENARIO_COMPLETED = "scenario_completed"
    SCENARIO_CANCELLED = "scenario_cancelled"
