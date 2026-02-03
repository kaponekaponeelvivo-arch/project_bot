from typing import Dict

from .states import ScenarioState
from core.scanner_core.events.event_types import EventType


TRANSITIONS: Dict[ScenarioState, Dict[EventType, ScenarioState]] = {

    # ===============================
    # START
    # ===============================
    ScenarioState.IDLE: {
        EventType.IMPULSE_DETECTED: ScenarioState.IMPULSE,
    },

    # ===============================
    # IMPULSE
    # ===============================
    ScenarioState.IMPULSE: {
        EventType.CORRECTION_STARTED: ScenarioState.CORRECTION,
        EventType.IMPULSE_EXHAUSTED: ScenarioState.CANCELLED,
        EventType.CONTEXT_INVALIDATED: ScenarioState.CANCELLED,
    },

    # ===============================
    # CORRECTION
    # ===============================
    ScenarioState.CORRECTION: {
        EventType.ZONE_TOUCHED: ScenarioState.REACTION,
        EventType.CONTEXT_INVALIDATED: ScenarioState.CANCELLED,
    },

    # ===============================
    # REACTION
    # ===============================
    ScenarioState.REACTION: {
        EventType.SCENARIO_CONFIRMED: ScenarioState.CONFIRMED,
        EventType.ZONE_INVALIDATED: ScenarioState.CANCELLED,
        EventType.CONTEXT_INVALIDATED: ScenarioState.CANCELLED,
    },

    # ===============================
    # CONFIRMED
    # ===============================
    ScenarioState.CONFIRMED: {
        EventType.SCENARIO_COMPLETED: ScenarioState.COMPLETED,
        EventType.CONTEXT_INVALIDATED: ScenarioState.CANCELLED,
    },

}
