from datetime import datetime, timedelta

from core.db.models.subscription import Subscription
from core.storage.postgres_subscriptions import PostgresSubscriptionsStorage
from core.services.users import UsersService


class SubscriptionsService:
    def __init__(self, users_service: UsersService):
        self.users_service = users_service
        self.subscriptions_storage = PostgresSubscriptionsStorage()

    # =========================
    # ADMIN выдача (НЕ реферальная)
    # =========================
    async def add_admin_subscription(
        self,
        telegram_id: int,
        days: int,
        plan: str,
    ):
        user = await self.users_service.get_user(telegram_id)
        if not user:
            return

        now = datetime.utcnow()
        expires_at = now + timedelta(days=days)

        subscription = Subscription(
            telegram_id=telegram_id,
            referrer_telegram_id=None,  # ❌ НЕ реферальная
            plan=plan,
            days=days,
            started_at=now,
            expires_at=expires_at,
        )

        await self.subscriptions_storage.add(subscription)

        if user.subscription_until and user.subscription_until > now:
            user.subscription_until += timedelta(days=days)
        else:
            user.subscription_until = expires_at

        user.subscription_plan = plan
        user.subscription_days_total += days

        await self.users_service.storage.update(user)

    # =========================
    # ПОКУПКА (реферальная)
    # =========================
    async def add_purchase_subscription(
        self,
        telegram_id: int,
        days: int,
        plan: str,
    ):
        user = await self.users_service.get_user(telegram_id)
        if not user:
            return

        now = datetime.utcnow()
        expires_at = now + timedelta(days=days)

        referrer_id = user.referred_by if user.referred_by else None

        subscription = Subscription(
            telegram_id=telegram_id,
            referrer_telegram_id=referrer_id,
            plan=plan,
            days=days,
            started_at=now,
            expires_at=expires_at,
        )

        await self.subscriptions_storage.add(subscription)

        if user.subscription_until and user.subscription_until > now:
            user.subscription_until += timedelta(days=days)
        else:
            user.subscription_until = expires_at

        user.subscription_plan = plan
        user.subscription_days_total += days

        await self.users_service.storage.update(user)

    async def remove_subscription(self, telegram_id: int):
        user = await self.users_service.get_user(telegram_id)
        if not user:
            return

        user.subscription_until = None
        user.subscription_plan = None
        user.subscription_days_total = 0

        await self.users_service.storage.update(user)
