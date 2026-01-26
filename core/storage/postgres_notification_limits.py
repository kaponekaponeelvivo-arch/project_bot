from datetime import date as date_type

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from core.db.models.notification_limit import NotificationLimit


class PostgresNotificationLimitsStorage:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_count(self, telegram_id: int, day: date_type) -> int:
        result = await self.session.execute(
            select(NotificationLimit.sent_count).where(
                NotificationLimit.telegram_id == telegram_id,
                NotificationLimit.date == day,
            )
        )
        return result.scalar_one_or_none() or 0

    async def ensure_row(self, telegram_id: int, day: date_type) -> None:
        result = await self.session.execute(
            select(NotificationLimit).where(
                NotificationLimit.telegram_id == telegram_id,
                NotificationLimit.date == day,
            )
        )
        if result.scalar_one_or_none() is None:
            self.session.add(
                NotificationLimit(
                    telegram_id=telegram_id,
                    date=day,
                    sent_count=0,
                )
            )
            await self.session.commit()

    async def increment(self, telegram_id: int, day: date_type) -> None:
        await self.ensure_row(telegram_id, day)

        await self.session.execute(
            update(NotificationLimit)
            .where(
                NotificationLimit.telegram_id == telegram_id,
                NotificationLimit.date == day,
            )
            .values(
                sent_count=NotificationLimit.sent_count + 1
            )
        )
        await self.session.commit()
