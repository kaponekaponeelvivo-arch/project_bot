from sqlalchemy import select
from core.db.database import AsyncSessionLocal
from core.db.models.user import User


class PostgresUsersStorage:
    def __init__(self):
        self.session_factory = AsyncSessionLocal

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
