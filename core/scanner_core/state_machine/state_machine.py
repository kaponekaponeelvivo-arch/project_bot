from typing import Optional
from core.scanner_core.state_machine.states import ScenarioState
from core.scanner_core.events.event_types import EventType


TRANSITIONS = {

    ScenarioState.IDLE: {
        EventType.MARKET_CONTEXT_CHANGED: ScenarioState.TREND_ACTIVE,
    },

    ScenarioState.TREND_ACTIVE: {
        EventType.IMPULSE_DETECTED: ScenarioState.IMPULSE,
        EventType.SCENARIO_CANCELLED: ScenarioState.CANCELLED,
    },

    ScenarioState.IMPULSE: {
        EventType.CORRECTION_STARTED: ScenarioState.CORRECTION,
        EventType.SCENARIO_CANCELLED: ScenarioState.CANCELLED,
    },

    ScenarioState.CORRECTION: {
        EventType.ZONE_REACTED: ScenarioState.REACTION,
        EventType.SCENARIO_CANCELLED: ScenarioState.CANCELLED,
    },

    ScenarioState.REACTION: {
        EventType.SCENARIO_CONFIRMED: ScenarioState.CONFIRMED,
        EventType.SCENARIO_CANCELLED: ScenarioState.CANCELLED,
    },

    ScenarioState.CONFIRMED: {
        EventType.SCENARIO_COMPLETED: ScenarioState.COMPLETED,
        EventType.SCENARIO_CANCELLED: ScenarioState.CANCELLED,
    },

    ScenarioState.COMPLETED: {},
    ScenarioState.CANCELLED: {},
}


class StateMachine:

    @staticmethod
    def can_transition(
        current_state: ScenarioState,
        event_type: EventType,
    ) -> bool:
        return event_type in TRANSITIONS.get(current_state, {})

    @staticmethod
    def next_state(
        current_state: ScenarioState,
        event_type: EventType,
    ) -> Optional[ScenarioState]:
        return TRANSITIONS.get(current_state, {}).get(event_type)
