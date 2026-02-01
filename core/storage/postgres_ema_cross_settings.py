from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from core.db.models.ema_cross_settings import EmaCrossSettings


class PostgresEmaCrossSettingsStorage:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_telegram_id(
        self,
        telegram_id: int,
    ) -> Optional[EmaCrossSettings]:
        stmt = select(EmaCrossSettings).where(
            EmaCrossSettings.telegram_id == telegram_id
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_default(
        self,
        telegram_id: int,
    ) -> EmaCrossSettings:
        settings = EmaCrossSettings(
            telegram_id=telegram_id,
            enabled=False,
            timeframe=None,
            modes=[],
        )
        self._session.add(settings)
        await self._session.commit()
        await self._session.refresh(settings)
        return settings

    async def get_or_create(
        self,
        telegram_id: int,
    ) -> EmaCrossSettings:
        settings = await self.get_by_telegram_id(telegram_id)
        if settings is not None:
            return settings
        return await self.create_default(telegram_id)

    async def update_enabled(
        self,
        telegram_id: int,
        enabled: bool,
    ) -> None:
        stmt = (
            update(EmaCrossSettings)
            .where(EmaCrossSettings.telegram_id == telegram_id)
            .values(enabled=enabled)
        )
        await self._session.execute(stmt)
        await self._session.commit()

    async def update_timeframe(
        self,
        telegram_id: int,
        timeframe: Optional[str],
    ) -> None:
        stmt = (
            update(EmaCrossSettings)
            .where(EmaCrossSettings.telegram_id == telegram_id)
            .values(
                timeframe=timeframe,
                modes=[],
            )
        )
        await self._session.execute(stmt)
        await self._session.commit()

    async def update_modes(
        self,
        telegram_id: int,
        modes: list[str],
    ) -> None:
        stmt = (
            update(EmaCrossSettings)
            .where(EmaCrossSettings.telegram_id == telegram_id)
            .values(modes=modes)
        )
        await self._session.execute(stmt)
        await self._session.commit()
