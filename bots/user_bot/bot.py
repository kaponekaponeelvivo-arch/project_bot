from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from datetime import datetime

from config.settings import settings
from bots.user_bot.menu import main_menu, plans_menu, back_menu

from core.storage.postgres_users import PostgresUsersStorage
from core.services.users import UsersService
from core.services.subscription_gate import SubscriptionGate


# ========= DEPENDENCIES =========

users_storage = PostgresUsersStorage()
users_service = UsersService(users_storage)
subscription_gate = SubscriptionGate(users_service)


# ========= HELPERS =========

async def send_main_menu(obj):
    user = await users_service.get_user(obj.from_user.id)
    has_subscription = (
        user.subscription_until and user.subscription_until > datetime.utcnow()
        if user else False
    )

    text = "👋 <b>Welcome to your dashboard</b>"
    keyboard = main_menu(has_subscription)

    if isinstance(obj, CallbackQuery):
        await obj.message.edit_text(
            text,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
        await obj.answer()
    else:
        await obj.answer(
            text,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )


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

    await send_main_menu(message)


async def menu_handler(callback: CallbackQuery):
    data = callback.data
    user = await users_service.get_user(callback.from_user.id)

    # ---------- MY SUBSCRIPTION ----------
    if data == "my_subscription":
        if user and user.subscription_until and user.subscription_until > datetime.utcnow():
            text = (
                "👤 <b>Your subscription</b>\n\n"
                "🟢 Status: Active\n"
                f"📅 Valid until: {user.subscription_until.strftime('%Y-%m-%d')}\n"
                f"📦 Plan: {user.subscription_plan}"
            )
        else:
            text = (
                "👤 <b>Your subscription</b>\n\n"
                "🔴 Status: Inactive\n"
                "💡 You don’t have an active subscription."
            )

        await callback.message.edit_text(
            text,
            reply_markup=back_menu(),
            parse_mode=ParseMode.HTML
        )
        await callback.answer()
        return

    # ---------- BUY / EXTEND ----------
    if data == "buy_subscription":
        await callback.message.edit_text(
            "💳 <b>Choose a subscription plan</b>",
            reply_markup=plans_menu(),
            parse_mode=ParseMode.HTML
        )
        await callback.answer()
        return

    if data.startswith("plan_"):
        days = data.replace("plan_", "")
        await callback.message.edit_text(
            f"💳 <b>Subscription {days} days</b>\n\n"
            "Payments will be available soon.\n"
            "Please check back later.",
            reply_markup=back_menu(),
            parse_mode=ParseMode.HTML
        )
        await callback.answer()
        return

    # ---------- SCREENERS ----------
    if data == "screeners":
        await callback.message.edit_text(
            "📡 <b>Screeners</b>\n\n"
            "Market screeners will be available soon.\n"
            "Stay tuned.",
            reply_markup=back_menu(),
            parse_mode=ParseMode.HTML
        )
        await callback.answer()
        return

    # ---------- ABOUT ----------
    if data == "about":
        await callback.message.edit_text(
            "🤖 <b>About screener</b>\n\n"
            "This bot detects market events:\n"
            "• volatility spikes\n"
            "• momentum changes\n"
            "• unusual activity\n\n"
            "It does NOT give buy/sell signals.\n"
            "You stay in control of decisions.",
            reply_markup=back_menu(),
            parse_mode=ParseMode.HTML
        )
        await callback.answer()
        return

    # ---------- REFERRALS ----------
    if data == "referrals":
        ref_link = f"https://t.me/{settings.user_bot_username}?start=ref_{user.telegram_id}"
        text = (
            "🎯 <b>Referral program</b>\n\n"
            "Invite users and earn rewards.\n\n"
            f"Your referral link:\n{ref_link}\n\n"
            f"👥 Invited users: <b>{user.referrals_count}</b>"
        )

        await callback.message.edit_text(
            text,
            reply_markup=back_menu(),
            parse_mode=ParseMode.HTML
        )
        await callback.answer()
        return

    # ---------- SUPPORT ----------
    if data == "support":
        await callback.message.edit_text(
            "🆘 <b>Support</b>\n\n"
            "If you have any issues with payments\n"
            "or subscription, please contact:\n\n"
            "@fake_support_account",
            reply_markup=back_menu(),
            parse_mode=ParseMode.HTML
        )
        await callback.answer()
        return

    # ---------- BACK ----------
    if data == "back_main":
        await send_main_menu(callback)
        return


# ========= BOT START =========

async def start_bot():
    bot = Bot(
        token=settings.user_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    dp = Dispatcher()

    dp.message.register(start_handler, CommandStart())
    dp.callback_query.register(menu_handler)

    await dp.start_polling(bot)
