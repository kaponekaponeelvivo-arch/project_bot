from sqlalchemy import Column, Integer, BigInteger, String, DateTime
from datetime import datetime

from core.db.database import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True)

    telegram_id = Column(BigInteger, index=True, nullable=False)
    referrer_telegram_id = Column(BigInteger, nullable=True)

    plan = Column(String, nullable=False)
    days = Column(Integer, nullable=False)

    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
