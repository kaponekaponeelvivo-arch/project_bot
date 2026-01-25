from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    telegram_id: int
    username: Optional[str]
    created_at: datetime
    is_active: bool = True
