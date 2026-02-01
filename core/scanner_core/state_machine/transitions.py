# core/scanner_core/state_machine/transitions.py
from typing import Dict

from .states import ScenarioState
from core.scanner_core.events.event_types import EventType


TRANSITIONS: Dict[ScenarioState, Dict[EventType, ScenarioState]] = {
    ScenarioState.IDLE: {
        EventType.TREND_DETECTED: ScenarioState.TREND_ACTIVE,
    },

    ScenarioState.TREND_ACTIVE: {
        EventType.IMPULSE_DETECTED: ScenarioState.IMPULSE,
        EventType.CONTEXT_INVALIDATED: ScenarioState.CANCELLED,
        EventType.MARKET_PHASE_CHANGED: ScenarioState.CANCELLED,
    },

    ScenarioState.IMPULSE: {
        EventType.CORRECTION_STARTED: ScenarioState.CORRECTION,
        EventType.RANGE_FORMED: ScenarioState.PAUSE,
        EventType.IMPULSE_EXHAUSTED: ScenarioState.CANCELLED,
    },

    ScenarioState.CORRECTION: {
        EventType.ZONE_TOUCHED: ScenarioState.REACTION,
        EventType.RANGE_FORMED: ScenarioState.PAUSE,
        EventType.CORRECTION_INVALID: ScenarioState.CANCELLED,
    },

    ScenarioState.PAUSE: {
        EventType.IMPULSE_DETECTED: ScenarioState.IMPULSE,
        EventType.ZONE_TOUCHED: ScenarioState.REACTION,
        EventType.RANGE_BROKEN: ScenarioState.CANCELLED,
    },

    ScenarioState.REACTION: {
        EventType.SCENARIO_CONFIRMED: ScenarioState.CONFIRMED,
        EventType.ZONE_INVALIDATED: ScenarioState.CANCELLED,
    },

    ScenarioState.CONFIRMED: {
        EventType.SCENARIO_COMPLETED: ScenarioState.COMPLETED,
        EventType.STRUCTURE_BROKEN: ScenarioState.CANCELLED,
        EventType.ZONE_INVALIDATED: ScenarioState.CANCELLED,
    },
}
