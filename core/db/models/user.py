from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    telegram_id = Column(BigInteger, primary_key=True, index=True)
    username = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # ===== SUBSCRIPTION =====
    subscription_until = Column(DateTime, nullable=True)
    subscription_plan = Column(String, nullable=True)  # "7d", "30d", "90d"
    subscription_days_total = Column(Integer, nullable=False, default=0)

    # ===== REFERRALS =====
    referred_by = Column(BigInteger, nullable=True)
    referrals_count = Column(Integer, nullable=False, default=0)
