from datetime import datetime
from core.db.models.user import User
from core.storage.postgres_users import PostgresUsersStorage


class UsersService:
    def __init__(self, storage: PostgresUsersStorage):
        self.storage = storage

    # ========= CRUD =========

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
            subscription_plan=None,
            subscription_days_total=0,
            referred_by=referred_by,
            referrals_count=0,
        )

        await self.storage.add(user)

        # referral counter
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

    # ========= ADMIN ACTIONS =========

    async def block_user(self, telegram_id: int):
        user = await self.get_user(telegram_id)
        if not user:
            return
        user.is_active = False
        await self.storage.update(user)

    async def unblock_user(self, telegram_id: int):
        user = await self.get_user(telegram_id)
        if not user:
            return
        user.is_active = True
        await self.storage.update(user)

    # ========= SUBSCRIPTIONS =========

    async def has_active_subscription(self, telegram_id: int) -> bool:
        user = await self.get_user(telegram_id)
        if not user or not user.subscription_until:
            return False
        return user.subscription_until > datetime.utcnow()
