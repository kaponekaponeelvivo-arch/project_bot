from enum import Enum


class ZoneType(Enum):
    """
    Logical reason why zone exists.
    Priority is NOT defined here.
    """
    IMBALANCE = "imbalance"      # FVG
    STRUCTURE = "structure"      # HL / LH
    RANGE = "range"              # Local range
    PERCENT = "percent"          # Fibo / percent correction
