from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config.settings import settings

from core.storage.postgres_users import PostgresUsersStorage
from core.services.users import UsersService
from core.services.subscription_gate import SubscriptionGate


# ========= DEPENDENCIES =========

users_storage = PostgresUsersStorage()
users_service = UsersService(users_storage)
subscription_gate = SubscriptionGate(users_service)


# ========= HANDLERS =========

async def start_handler(message: Message):
    args = message.text.split()
    referred_by = None

    if len(args) > 1 and args[1].startswith("ref_"):
        try:
            referred_by = int(args[1].replace("ref_", ""))
        except ValueError:
            referred_by = None

    user = await users_service.get_user(message.from_user.id)

    if not user:
        await users_service.create_user(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            referred_by=referred_by,
        )

    await message.answer(
        "👋 <b>Welcome</b>\n\n"
        "Use /ref to get your referral link.",
        parse_mode=ParseMode.HTML
    )


async def ref_handler(message: Message):
    user = await users_service.get_user(message.from_user.id)

    if not user:
        await message.answer("User not found")
        return

    ref_link = f"https://t.me/{settings.user_bot_username}?start=ref_{user.telegram_id}"

    await message.answer(
        "🎯 <b>Your referral link</b>\n\n"
        f"{ref_link}\n\n"
        f"👥 Invited users: <b>{user.referrals_count}</b>",
        parse_mode=ParseMode.HTML
    )


# ========= BOT START =========

async def start_bot():
    bot = Bot(
        token=settings.user_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    dp = Dispatcher()

    dp.message.register(start_handler, CommandStart())
    dp.message.register(ref_handler, lambda m: m.text == "/ref")

    await dp.start_polling(bot)
