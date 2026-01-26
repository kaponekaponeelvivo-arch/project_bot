from sqlalchemy import select
from core.db.database import AsyncSessionLocal
from core.db.models.subscription import Subscription


class PostgresSubscriptionsStorage:
    def __init__(self):
        self.session_factory = AsyncSessionLocal

    async def add(self, subscription: Subscription):
        async with self.session_factory() as session:
            session.add(subscription)
            await session.commit()

    async def get_by_user(self, telegram_id: int) -> list[Subscription]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(Subscription).where(
                    Subscription.telegram_id == telegram_id
                )
            )
            return result.scalars().all()

    async def all(self) -> list[Subscription]:
        async with self.session_factory() as session:
            result = await session.execute(select(Subscription))
            return result.scalars().all()
