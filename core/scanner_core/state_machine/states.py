# core/scanner_core/state_machine/states.py
from enum import Enum


class ScenarioState(Enum):
    IDLE = "idle"
    TREND_ACTIVE = "trend_active"
    IMPULSE = "impulse"
    CORRECTION = "correction"
    PAUSE = "pause"
    REACTION = "reaction"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
