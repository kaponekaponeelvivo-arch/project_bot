from dataclasses import dataclass
from enum import Enum
from typing import Literal


class Timeframe(str, Enum):
    M15 = "15m"
    H1 = "1h"
    H4 = "4h"
    D1 = "1d"


class CrossStatus(str, Enum):
    START = "start"
    STRENGTHEN = "strengthen"
    EXTREME = "extreme"


class Direction(str, Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"


@dataclass(frozen=True)
class EmaCrossEvent:
    symbol: str
    timeframe: Timeframe
    mode: str
    status: CrossStatus
    direction: Direction
    context: str
