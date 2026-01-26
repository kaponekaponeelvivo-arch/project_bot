import asyncio

from bots.admin_bot.bot import start_bot as start_admin_bot
from bots.user_bot.bot import start_bot as start_user_bot


async def main():
    await asyncio.gather(
        start_admin_bot(),
        start_user_bot(),
    )


if __name__ == "__main__":
    asyncio.run(main())
