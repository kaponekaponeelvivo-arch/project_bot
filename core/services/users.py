from datetime import datetime, timedelta
from core.db.models.user import User
from core.storage.postgres_users import PostgresUsersStorage


class UsersService:
    def __init__(self):
        self.storage = PostgresUsersStorage()

    async def create_user(
        self,
        telegram_id: int,
        username: str | None,
        referred_by: int | None = None,
    ) -> User:
        user = User(
            telegram_id=telegram_id,
            username=username,
            created_at=datetime.utcnow(),
            is_active=True,
            subscription_until=None,
            referred_by=referred_by,
            referrals_count=0,
        )

        await self.storage.add(user)

        if referred_by:
            referrer = await self.storage.get(referred_by)
            if referrer:
                referrer.referrals_count += 1
                await self.storage.update(referrer)

        return user

    async def get_user(self, telegram_id: int) -> User | None:
        return await self.storage.get(telegram_id)

    async def get_all_users(self):
        return await self.storage.all()

    async def block_user(self, telegram_id: int):
        user = await self.get_user(telegram_id)
        if user:
            user.is_active = False
            await self.storage.update(user)

    async def unblock_user(self, telegram_id: int):
        user = await self.get_user(telegram_id)
        if user:
            user.is_active = True
            await self.storage.update(user)

    async def give_subscription(self, telegram_id: int, days: int):
        user = await self.get_user(telegram_id)
        if not user:
            return

        now = datetime.utcnow()

        if user.subscription_until and user.subscription_until > now:
            user.subscription_until += timedelta(days=days)
        else:
            user.subscription_until = now + timedelta(days=days)

        await self.storage.update(user)

    async def remove_subscription(self, telegram_id: int):
        user = await self.get_user(telegram_id)
        if user:
            user.subscription_until = None
            await self.storage.update(user)

    async def has_active_subscription(self, telegram_id: int) -> bool:
        user = await self.get_user(telegram_id)
        if not user or not user.subscription_until:
            return False
        return user.subscription_until > datetime.utcnow()
