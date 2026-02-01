from sqlalchemy import (
    Column,
    BigInteger,
    Boolean,
    String,
    DateTime,
)
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime

from core.db.database import Base


class EmaCrossSettings(Base):
    __tablename__ = "ema_cross_settings"

    telegram_id = Column(BigInteger, primary_key=True)

    enabled = Column(Boolean, nullable=False, default=False)
    timeframe = Column(String, nullable=True)

    modes = Column(JSONB, nullable=False, default=list)

    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
