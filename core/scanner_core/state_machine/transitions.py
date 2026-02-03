from typing import Dict

from .states import ScenarioState
from core.scanner_core.events.event_types import EventType


TRANSITIONS: Dict[ScenarioState, Dict[EventType, ScenarioState]] = {

    # ==================================
    # IDLE → TREND
    # ==================================
    ScenarioState.IDLE: {
        EventType.MARKET_CONTEXT_CHANGED: ScenarioState.TREND_ACTIVE,
    },

    # ==================================
    # TREND → IMPULSE (KEY TRANSITION)
    # ==================================
    ScenarioState.TREND_ACTIVE: {
        EventType.SCENARIO_STARTED: ScenarioState.IMPULSE,
        EventType.CONTEXT_INVALIDATED: ScenarioState.CANCELLED,
    },

    # ==================================
    # IMPULSE → CORRECTION / CANCELLED
    # ==================================
    ScenarioState.IMPULSE: {
        EventType.CORRECTION_STARTED: ScenarioState.CORRECTION,
        EventType.IMPULSE_EXHAUSTED: ScenarioState.CANCELLED,
    },

    # ==================================
    # CORRECTION → REACTION / PAUSE
    # ==================================
    ScenarioState.CORRECTION: {
        EventType.ZONE_REACTED: ScenarioState.REACTION,
        EventType.ZONE_INVALIDATED: ScenarioState.CANCELLED,
    },

    # ==================================
    # REACTION → CONFIRMED / CANCELLED
    # ==================================
    ScenarioState.REACTION: {
        EventType.SCENARIO_CONFIRMED: ScenarioState.CONFIRMED,
        EventType.ZONE_INVALIDATED: ScenarioState.CANCELLED,
    },

    # ==================================
    # CONFIRMED → COMPLETED / CANCELLED
    # ==================================
    ScenarioState.CONFIRMED: {
        EventType.SCENARIO_COMPLETED: ScenarioState.COMPLETED,
        EventType.STRUCTURE_BROKEN: ScenarioState.CANCELLED,
    },
}
