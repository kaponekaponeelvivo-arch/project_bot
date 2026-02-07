from enum import IntEnum


class WatchPriority(IntEnum):
    CONFIRMED = 1
    REACTION = 2
    CORRECTION = 3
    IMPULSE = 4
    TREND = 5
