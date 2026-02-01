# core/scanner_core/events/event.py
from dataclasses import dataclass, field
from typing import Any, Dict
from datetime import datetime

from .event_types import EventType


@dataclass(frozen=True)
class Event:
    """
    Immutable event object.
    Event is a fact. It happens once and never changes.
    """
    type: EventType
    symbol: str                     # e.g. "SOLUSDT"
    payload: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
