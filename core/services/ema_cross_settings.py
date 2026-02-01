from typing import List

from core.storage.postgres_ema_cross_settings import (
    PostgresEmaCrossSettingsStorage,
)
from core.db.models.ema_cross_settings import EmaCrossSettings


class EmaCrossSettingsService:
    MAX_MODES = 2

    def __init__(
        self,
        storage: PostgresEmaCrossSettingsStorage,
    ):
        self._storage = storage

    # ----------------------------
    # Base
    # ----------------------------

    async def get_settings(
        self,
        telegram_id: int,
    ) -> EmaCrossSettings:
        """
        Always returns settings.
        Creates default row if missing.
        """
        return await self._storage.get_or_create(telegram_id)

    # ----------------------------
    # Enabled / Disabled
    # ----------------------------

    async def enable(
        self,
        telegram_id: int,
    ) -> None:
        await self._storage.get_or_create(telegram_id)
        await self._storage.update_enabled(telegram_id, True)

    async def disable(
        self,
        telegram_id: int,
    ) -> None:
        await self._storage.get_or_create(telegram_id)
        await self._storage.update_enabled(telegram_id, False)

    # ----------------------------
    # Timeframe
    # ----------------------------

    async def set_timeframe(
        self,
        telegram_id: int,
        timeframe: str,
    ) -> None:
        """
        Sets timeframe and resets modes.
        """
        await self._storage.get_or_create(telegram_id)
        await self._storage.update_timeframe(telegram_id, timeframe)

    # ----------------------------
    # Modes
    # ----------------------------

    async def add_mode(
        self,
        telegram_id: int,
        mode: str,
    ) -> None:
        settings = await self._storage.get_or_create(telegram_id)

        if mode in settings.modes:
            return

        if len(settings.modes) >= self.MAX_MODES:
            raise ValueError("Maximum number of modes reached")

        new_modes = list(settings.modes)
        new_modes.append(mode)

        await self._storage.update_modes(telegram_id, new_modes)

    async def remove_mode(
        self,
        telegram_id: int,
        mode: str,
    ) -> None:
        settings = await self._storage.get_or_create(telegram_id)

        if mode not in settings.modes:
            return

        new_modes = [m for m in settings.modes if m != mode]

        await self._storage.update_modes(telegram_id, new_modes)

    async def set_modes(
        self,
        telegram_id: int,
        modes: List[str],
    ) -> None:
        """
        Explicitly sets modes list (used by UX reset logic).
        """
        if len(modes) > self.MAX_MODES:
            raise ValueError("Maximum number of modes reached")

        await self._storage.get_or_create(telegram_id)
        await self._storage.update_modes(telegram_id, modes)
