from enum import IntEnum
from core.scanner_core.state_machine import ScenarioState


class WatchPriority(IntEnum):
    CONFIRMED = 1
    REACTION = 2
    CORRECTION = 3
    IMPULSE = 4
    TREND_ACTIVE = 5


STATE_TO_PRIORITY = {
    ScenarioState.CONFIRMED: WatchPriority.CONFIRMED,
    ScenarioState.REACTION: WatchPriority.REACTION,
    ScenarioState.CORRECTION: WatchPriority.CORRECTION,
    ScenarioState.IMPULSE: WatchPriority.IMPULSE,
    ScenarioState.TREND_ACTIVE: WatchPriority.TREND_ACTIVE,
}
