from sqlalchemy import select, func, desc
from core.db.database import AsyncSessionLocal
from core.db.models.user import User
from core.db.models.subscription import Subscription


class PostgresUsersStorage:
    def __init__(self):
        self.session_factory = AsyncSessionLocal

    # ---------- базовые операции ----------

    async def add(self, user: User):
        async with self.session_factory() as session:
            session.add(user)
            await session.commit()

    async def get(self, telegram_id: int) -> User | None:
        async with self.session_factory() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            return result.scalar_one_or_none()

    async def all(self) -> list[User]:
        async with self.session_factory() as session:
            result = await session.execute(select(User))
            return result.scalars().all()

    async def update(self, user: User):
        async with self.session_factory() as session:
            await session.merge(user)
            await session.commit()

    # ---------- реферальная аналитика ----------

    async def total_ref_joins(self) -> int:
        async with self.session_factory() as session:
            result = await session.execute(
                select(func.count()).select_from(User).where(User.referred_by.isnot(None))
            )
            return result.scalar_one()

    async def total_ref_purchases(self) -> int:
        async with self.session_factory() as session:
            result = await session.execute(
                select(func.count())
                .select_from(Subscription)
                .where(Subscription.referrer_telegram_id.isnot(None))
            )
            return result.scalar_one()

    async def top_referrers(self, limit: int = 10) -> list[tuple[int, int]]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(
                    Subscription.referrer_telegram_id,
                    func.count().label("cnt"),
                )
                .where(Subscription.referrer_telegram_id.isnot(None))
                .group_by(Subscription.referrer_telegram_id)
                .order_by(desc("cnt"))
                .limit(limit)
            )
            return result.all()

    async def purchases_by_plan(self, telegram_id: int) -> dict[str, int]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(
                    Subscription.plan,
                    func.count()
                )
                .where(Subscription.referrer_telegram_id == telegram_id)
                .group_by(Subscription.plan)
            )
            return {plan: count for plan, count in result.all()}
