from datetime import datetime

from core.db.models.user import User
from core.storage.postgres_users import PostgresUsersStorage


class UsersService:
    def __init__(self, storage: PostgresUsersStorage):
        self.storage = storage

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

        # referral logic
        if referred_by:
            referrer = await self.storage.get(referred_by)
            if referrer:
                referrer.referrals_count += 1
                await self.storage.update(referrer)

        return user

    async def get_user(self, telegram_id: int) -> User | None:
        return await self.storage.get(telegram_id)

    async def get_all_users(self):
        return await self.storage.get_all()

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
