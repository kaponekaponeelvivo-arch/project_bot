# core/scanner_core/market_context/context.py
from dataclasses import dataclass
from enum import Enum


class MarketPhase(Enum):
    TREND_UP = "trend_up"
    TREND_DOWN = "trend_down"
    RANGE = "range"


class ContextValidity(Enum):
    VALID = "valid"
    INVALID = "invalid"


@dataclass
class MarketContext:
    phase: MarketPhase
    validity: ContextValidity
