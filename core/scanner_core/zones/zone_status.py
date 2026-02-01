from enum import Enum


class ZoneStatus(Enum):
    ACTIVE = "active"
    TOUCHED = "touched"
    REACTED = "reacted"
    INVALIDATED = "invalidated"
