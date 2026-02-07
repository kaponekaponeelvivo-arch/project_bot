from dataclasses import dataclass
from datetime import datetime


@dataclass
class WatchlistItem:
    symbol: str
    state: str
    updated_at: datetime
