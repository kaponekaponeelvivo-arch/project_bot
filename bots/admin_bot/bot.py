import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode


async def start_bot():
    bot = Bot(
        token="TEST_TOKEN",
        parse_mode=ParseMode.HTML
    )

    dp = Dispatcher()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(start_bot())
