# core/scanner_core/events/event_types.py
from enum import Enum


class EventType(Enum):
    # Market / Context
    MARKET_PHASE_CHANGED = "market_phase_changed"
    CONTEXT_INVALIDATED = "context_invalidated"
    CONTEXT_RESTORED = "context_restored"

    # Structure / Trend
    TREND_DETECTED = "trend_detected"
    STRUCTURE_BROKEN = "structure_broken"

    # Impulse
    IMPULSE_DETECTED = "impulse_detected"
    IMPULSE_EXHAUSTED = "impulse_exhausted"

    # Correction / Range
    CORRECTION_STARTED = "correction_started"
    CORRECTION_INVALID = "correction_invalid"
    RANGE_FORMED = "range_formed"
    RANGE_BROKEN = "range_broken"

    # Zones
    ZONE_CREATED = "zone_created"
    ZONE_TOUCHED = "zone_touched"
    ZONE_REACTED = "zone_reacted"
    ZONE_INVALIDATED = "zone_invalidated"

    # Scenario (public)
    SCENARIO_STARTED = "scenario_started"
    SCENARIO_CONFIRMED = "scenario_confirmed"
    SCENARIO_COMPLETED = "scenario_completed"
    SCENARIO_CANCELLED = "scenario_cancelled"
