from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, BaseFilter
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from datetime import datetime

from config.settings import settings
from bots.admin_bot.menu import (
    main_menu_keyboard,
    back_keyboard,
    users_list_keyboard,
    user_card_keyboard,
)

from core.storage.postgres_users import PostgresUsersStorage
from core.services.users import UsersService
from core.services.subscriptions import SubscriptionsService


# ========= SERVICES =========

users_storage = PostgresUsersStorage()
users_service = UsersService(users_storage)
subscriptions_service = SubscriptionsService(users_storage)


# ========= FILTERS =========

class AdminOnlyFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id == settings.admin_telegram_id


class AdminOnlyCallbackFilter(BaseFilter):
    async def __call__(self, callback: CallbackQuery) -> bool:
        return callback.from_user.id == settings.admin_telegram_id


# ========= HELPERS =========

async def render_user_card(callback: CallbackQuery, telegram_id: int):
    user = await users_service.get_user(telegram_id)

    if not user:
        await callback.answer("User not found", show_alert=True)
        return

    now = datetime.utcnow()

    if user.subscription_until:
        if user.subscription_until > now:
            sub_status = f"🟢 Active until {user.subscription_until.strftime('%Y-%m-%d')}"
        else:
            sub_status = f"🔴 Expired ({user.subscription_until.strftime('%Y-%m-%d')})"
    else:
        sub_status = "❌ No subscription"

    text = (
        "👤 <b>User card</b>\n\n"
        f"ID: <b>{user.telegram_id}</b>\n"
        f"Username: @{user.username or '-'}\n"
        f"Status: {'🟢 Active' if user.is_active else '🔴 Blocked'}\n\n"
        f"💳 Subscription:\n{sub_status}"
    )

    await callback.message.edit_text(
        text,
        reply_markup=user_card_keyboard(user)
    )
    await callback.answer()


# ========= HANDLERS =========

async def start_handler(message: Message):
    if not await users_service.get_user(message.from_user.id):
        await users_service.create_user(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
        )

    await message.answer(
        "✅ <b>Admin panel</b>\n\nChoose a section:",
        reply_markup=main_menu_keyboard()
    )


async def menu_handler(callback: CallbackQuery):
    section = callback.data.replace("menu_", "")

    if section == "users":
        users = await users_service.get_all_users()

        if not users:
            await callback.message.edit_text(
                "📊 <b>Users</b>\n\nNo users yet.",
                reply_markup=back_keyboard()
            )
        else:
            await callback.message.edit_text(
                "📊 <b>Users</b>\n\nSelect user:",
                reply_markup=users_list_keyboard(users)
            )

        await callback.answer()
        return

    texts = {
        "subscriptions": "💳 <b>Subscriptions</b>\n\nIn development.",
        "screeners": "🤖 <b>Screeners</b>\n\nIn development.",
        "referrals": "🎯 <b>Referrals</b>\n\nIn development.",
        "stats": "📈 <b>Stats</b>\n\nIn development.",
        "system": "⚙️ <b>System</b>\n\nIn development.",
    }

    if section in texts:
        await callback.message.edit_text(
            texts[section],
            reply_markup=back_keyboard()
        )

    await callback.answer()


async def user_open_handler(callback: CallbackQuery):
    telegram_id = int(callback.data.split(":")[1])
    await render_user_card(callback, telegram_id)


async def user_block_handler(callback: CallbackQuery):
    telegram_id = int(callback.data.split(":")[1])
    await users_service.block_user(telegram_id)
    await render_user_card(callback, telegram_id)


async def user_unblock_handler(callback: CallbackQuery):
    telegram_id = int(callback.data.split(":")[1])
    await users_service.unblock_user(telegram_id)
    await render_user_card(callback, telegram_id)


# ===== SUBSCRIPTIONS =====

async def user_sub_add_handler(callback: CallbackQuery):
    _, days, telegram_id = callback.data.split(":")
    await subscriptions_service.add_subscription(
        telegram_id=int(telegram_id),
        days=int(days),
    )
    await render_user_card(callback, int(telegram_id))


async def user_sub_remove_handler(callback: CallbackQuery):
    telegram_id = int(callback.data.split(":")[1])
    await subscriptions_service.remove_subscription(telegram_id)
    await render_user_card(callback, telegram_id)


async def back_to_menu_handler(callback: CallbackQuery):
    await callback.message.edit_text(
        "✅ <b>Admin panel</b>\n\nChoose a section:",
        reply_markup=main_menu_keyboard()
    )
    await callback.answer()


# ========= BOT START =========

async def start_bot():
    bot = Bot(
        token=settings.admin_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    dp = Dispatcher()

    dp.message.register(start_handler, CommandStart(), AdminOnlyFilter())

    dp.callback_query.register(
        menu_handler,
        lambda c: c.data.startswith("menu_") and c.data != "menu_back",
        AdminOnlyCallbackFilter()
    )

    dp.callback_query.register(
        user_open_handler,
        lambda c: c.data.startswith("user_open:"),
        AdminOnlyCallbackFilter()
    )

    dp.callback_query.register(
        user_block_handler,
        lambda c: c.data.startswith("user_block:"),
        AdminOnlyCallbackFilter()
    )

    dp.callback_query.register(
        user_unblock_handler,
        lambda c: c.data.startswith("user_unblock:"),
        AdminOnlyCallbackFilter()
    )

    dp.callback_query.register(
        user_sub_add_handler,
        lambda c: c.data.startswith("user_sub_add:"),
        AdminOnlyCallbackFilter()
    )

    dp.callback_query.register(
        user_sub_remove_handler,
        lambda c: c.data.startswith("user_sub_remove:"),
        AdminOnlyCallbackFilter()
    )

    dp.callback_query.register(
        back_to_menu_handler,
        lambda c: c.data == "menu_back",
        AdminOnlyCallbackFilter()
    )

    await dp.start_polling(bot)
