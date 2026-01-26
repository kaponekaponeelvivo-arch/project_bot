from datetime import datetime, timedelta

from core.storage.postgres_users import PostgresUsersStorage


class SubscriptionsService:
    def __init__(self, users_storage: PostgresUsersStorage):
        self.users_storage = users_storage

    async def add_subscription(self, telegram_id: int, days: int) -> None:
        """
        Add or extend subscription for user.
        If subscription is active — extend from current expiration date.
        If expired or missing — start from now.
        """
        user = await self.users_storage.get(telegram_id)
        if not user:
            return

        now = datetime.utcnow()

        if user.subscription_until and user.subscription_until > now:
            new_until = user.subscription_until + timedelta(days=days)
        else:
            new_until = now + timedelta(days=days)

        await self.users_storage.update_subscription(
            telegram_id=telegram_id,
            subscription_until=new_until,
            subscription_days=days,
        )

    async def remove_subscription(self, telegram_id: int) -> None:
        """
        Remove subscription completely.
        """
        await self.users_storage.update_subscription(
            telegram_id=telegram_id,
            subscription_until=None,
            subscription_days=None,
        )

    async def has_active_subscription(self, telegram_id: int) -> bool:
        """
        Check if user has active subscription.
        """
        user = await self.users_storage.get(telegram_id)
        if not user or not user.subscription_until:
            return False

        return user.subscription_until > datetime.utcnow()
