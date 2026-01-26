from sqlalchemy import select
from core.db.models.user import User
from core.db.database import AsyncSessionLocal


class PostgresUsersStorage:
    def __init__(self):
        self.session_factory = AsyncSessionLocal

    async def add(self, user: User) -> None:
        async with self.session_factory() as session:
            session.add(user)
            await session.commit()

    async def get(self, telegram_id: int) -> User | None:
        async with self.session_factory() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            return result.scalar_one_or_none()

    async def get_all(self):
        async with self.session_factory() as session:
            result = await session.execute(
                select(User).order_by(User.created_at.desc())
            )
            return result.scalars().all()

    async def update(self, user: User) -> None:
        async with self.session_factory() as session:
            await session.merge(user)
            await session.commit()

    # ✅ НОВЫЙ МЕТОД — ДЛЯ SUBSCRIPTIONS SERVICE
    async def update_subscription(
        self,
        telegram_id: int,
        subscription_until,
        subscription_days: int | None = None,
    ) -> None:
        async with self.session_factory() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                return

            user.subscription_until = subscription_until
            await session.commit()
