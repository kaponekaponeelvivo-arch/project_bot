from datetime import datetime, timedelta

from core.services.users import UsersService


class SubscriptionsService:
    def __init__(self, users_service: UsersService):
        self.users_service = users_service

    async def add_subscription(
        self,
        telegram_id: int,
        days: int,
        plan: str,
    ):
        user = await self.users_service.get_user(telegram_id)
        if not user:
            return

        now = datetime.utcnow()

        # ===== subscription_until =====
        if user.subscription_until and user.subscription_until > now:
            user.subscription_until += timedelta(days=days)
        else:
            user.subscription_until = now + timedelta(days=days)

        # ===== subscription_days_total =====
        if user.subscription_days_total is None:
            user.subscription_days_total = 0

        user.subscription_days_total += days

        # ===== subscription_plan =====
        user.subscription_plan = plan

        await self.users_service.storage.update(user)

    async def remove_subscription(self, telegram_id: int):
        user = await self.users_service.get_user(telegram_id)
        if not user:
            return

        user.subscription_until = None
        user.subscription_plan = None

        await self.users_service.storage.update(user)
