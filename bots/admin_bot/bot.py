import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from config.settings import settings


async def start_bot():
    bot = Bot(
        token=settings.admin_bot_token,
        parse_mode=ParseMode.HTML
    )

    dp = Dispatcher()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(start_bot())
