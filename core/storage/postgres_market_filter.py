from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from core.db.models.market_filter import MarketFilter


class PostgresMarketFilterStorage:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, telegram_id: int) -> MarketFilter | None:
        result = await self.session.execute(
            select(MarketFilter).where(
                MarketFilter.telegram_id == telegram_id
            )
        )
        return result.scalar_one_or_none()

    async def create_default(self, telegram_id: int) -> None:
        mf = MarketFilter(
            telegram_id=telegram_id,
            mode="ALL",
            symbols=None,
            updated_at=datetime.utcnow(),
        )
        self.session.add(mf)
        await self.session.commit()

    async def update_mode(self, telegram_id: int, mode: str) -> None:
        await self.session.execute(
            update(MarketFilter)
            .where(MarketFilter.telegram_id == telegram_id)
            .values(
                mode=mode,
                symbols=None,
                updated_at=datetime.utcnow(),
            )
        )
        await self.session.commit()

    async def add_symbol(self, telegram_id: int, symbol: str) -> None:
        mf = await self.get(telegram_id)
        if mf is None:
            return

        symbols = mf.symbols or []
        if symbol not in symbols:
            symbols.append(symbol)

        await self.session.execute(
            update(MarketFilter)
            .where(MarketFilter.telegram_id == telegram_id)
            .values(
                symbols=symbols,
                updated_at=datetime.utcnow(),
            )
        )
        await self.session.commit()

    async def remove_symbol(self, telegram_id: int, symbol: str) -> None:
        mf = await self.get(telegram_id)
        if mf is None or not mf.symbols:
            return

        symbols = [s for s in mf.symbols if s != symbol]

        await self.session.execute(
            update(MarketFilter)
            .where(MarketFilter.telegram_id == telegram_id)
            .values(
                symbols=symbols,
                updated_at=datetime.utcnow(),
            )
        )
        await self.session.commit()

    async def clear_symbols(self, telegram_id: int) -> None:
        await self.session.execute(
            update(MarketFilter)
            .where(MarketFilter.telegram_id == telegram_id)
            .values(
                symbols=[],
                updated_at=datetime.utcnow(),
            )
        )
        await self.session.commit()
