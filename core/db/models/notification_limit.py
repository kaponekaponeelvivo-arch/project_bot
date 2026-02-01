from datetime import date

from sqlalchemy import BigInteger, Integer, Date
from sqlalchemy.orm import Mapped, mapped_column

from core.db.database import Base


class NotificationLimit(Base):
    __tablename__ = "notification_limits"

    telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
    )

    date: Mapped[date] = mapped_column(
        Date,
        primary_key=True,
    )	

    sent_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
