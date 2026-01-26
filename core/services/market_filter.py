from enum import Enum

from core.storage.postgres_market_filter import PostgresMarketFilterStorage


class MarketFilterMode(str, Enum):
    ALL = "ALL"
    SELECTED = "SELECTED"
    TOP_20 = "TOP_20"
    TOP_50 = "TOP_50"
    TOP_100 = "TOP_100"


class MarketFilterService:
    def __init__(self, storage: PostgresMarketFilterStorage):
        self.storage = storage

    async def ensure_exists(self, telegram_id: int) -> None:
        mf = await self.storage.get(telegram_id)
        if mf is None:
            await self.storage.create_default(telegram_id)

    async def get_state(self, telegram_id: int):
        await self.ensure_exists(telegram_id)
        return await self.storage.get(telegram_id)

    async def set_mode(self, telegram_id: int, mode: MarketFilterMode) -> None:
        await self.ensure_exists(telegram_id)
        await self.storage.update_mode(telegram_id, mode.value)

    async def add_symbol(self, telegram_id: int, symbol: str) -> None:
        await self.ensure_exists(telegram_id)
        await self.storage.update_mode(telegram_id, MarketFilterMode.SELECTED.value)
        await self.storage.add_symbol(telegram_id, symbol.upper())

    async def remove_symbol(self, telegram_id: int, symbol: str) -> None:
        await self.storage.remove_symbol(telegram_id, symbol.upper())

    async def clear_symbols(self, telegram_id: int) -> None:
        await self.storage.clear_symbols(telegram_id)

    async def get_symbols(self, telegram_id: int) -> list[str]:
        mf = await self.get_state(telegram_id)

        if mf.mode == MarketFilterMode.ALL.value:
            return []  # ALL MARKET — источник выше

        if mf.mode == MarketFilterMode.SELECTED.value:
            return mf.symbols or []

        if mf.mode in {
            MarketFilterMode.TOP_20.value,
            MarketFilterMode.TOP_50.value,
            MarketFilterMode.TOP_100.value,
        }:
            return []  # TOP списки — внешний провайдер (V1 заглушка)

        return []
