from sqlalchemy import BigInteger, String, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from core.db.database import Base


class MarketFilter(Base):
    __tablename__ = "market_filters"

    telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
    )

    mode: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    symbols: Mapped[list[str] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )
