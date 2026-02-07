from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

from .zone_types import ZoneType
from .zone_status import ZoneStatus


@dataclass
class Zone:
    """
    Zone is an AREA, not a price level.
    """

    zone_type: ZoneType

    id: str = field(default_factory=lambda: str(uuid4()))
    status: ZoneStatus = ZoneStatus.ACTIVE

    price_from: float = 0.0
    price_to: float = 0.0

    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def set_status(self, new_status: ZoneStatus) -> None:
        if self.status != new_status:
            self.status = new_status
            self.updated_at = datetime.utcnow()
