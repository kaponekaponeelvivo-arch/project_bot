# core/scanner_core/state_machine/state_machine.py

from core.scanner_core.state_machine.states import ScenarioState


class StateMachine:
    """
    Structural phase validator.

    This FSM no longer manages linear transitions.
    It only validates that a target phase is allowed
    in the structural model.

    Market structure is source of truth.
    """

    # ==========================================================
    # VALIDATION
    # ==========================================================
    @staticmethod
    def is_valid(target_state: ScenarioState) -> bool:
        """
        Validates that target phase exists
        in structural lifecycle model.
        """

        allowed_states = {
            ScenarioState.IDLE,
            ScenarioState.TREND_ACTIVE,
            ScenarioState.IMPULSE,
            ScenarioState.CORRECTION,
            ScenarioState.REACTION,
            ScenarioState.CONFIRMED,
            ScenarioState.CANCELLED,
            ScenarioState.COMPLETED,
        }

        return target_state in allowed_states
