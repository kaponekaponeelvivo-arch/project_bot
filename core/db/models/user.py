from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    # Telegram
    telegram_id = Column(BigInteger, primary_key=True, index=True)
    username = Column(String, nullable=True)

    # System
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Subscription
    subscription_until = Column(DateTime, nullable=True)
    subscription_days = Column(Integer, nullable=True)  # NEW

    # Referrals
    referred_by = Column(BigInteger, nullable=True)
    referrals_count = Column(Integer, default=0)
