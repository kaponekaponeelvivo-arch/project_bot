# core/scanner_core/impulse/impulse.py
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Impulse:
    """
    Impulse is a fixed directional move.
    Once created, it never changes.
    """
    direction: str              # "LONG" or "SHORT"
    start_price: float
    end_price: float
    started_at: datetime
    finished_at: datetime
