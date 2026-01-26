from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    telegram_id: int
    username: Optional[str]
    created_at: datetime
    is_active: bool = True

    subscription_until: Optional[datetime] = None

    # ===== REFERRALS =====
    referred_by: Optional[int] = None
    referrals_count: int = 0
