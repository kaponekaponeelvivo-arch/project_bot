from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, BaseFilter
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config.settings import settings
from bots.admin_bot.menu import (
    main_menu_keyboard,
    back_keyboard,
    users_list_keyboard,
    user_card_keyboard,
)

from core.storage.users import UsersStorage
from core.services.users import UsersService


users_storage = UsersStorage()
users_service = UsersService(users_storage)


class AdminOnlyFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id == settings.admin_telegram_id


class AdminOnlyCallbackFilter(BaseFilter):
    async def __call__(self, callback: CallbackQuery) -> bool:
        return callback.from_user.id == settings.admin_telegram_id


async def start_handler(message: Message):
    if not users_service.get_user(message.from_user.id):
        users_service.create_user(
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
        users = users_service.get_all_users()

        if not users:
            await callback.message.edit_text(
                "📊 <b>Users</b>\n\nПользователей пока нет.",
                reply_markup=back_keyboard()
            )
        else:
            await callback.message.edit_text(
                "📊 <b>Users</b>\n\nВыбери пользователя:",
                reply_markup=users_list_keyboard(users)
            )

        await callback.answer()
        return

    texts = {
        "subscriptions": "💳 <b>Subscriptions</b>\n\nВ разработке.",
        "screeners": "🤖 <b>Screeners</b>\n\nВ разработке.",
        "referrals": "🎯 <b>Referrals</b>\n\nВ разработке.",
        "stats": "📈 <b>Stats</b>\n\nВ разработке.",
        "system": "⚙️ <b>System</b>\n\nВ разработке.",
    }

    await callback.message.edit_text(
        texts.get(section, "Unknown section"),
        reply_markup=back_keyboard()
    )
    await callback.answer()


async def user_open_handler(callback: CallbackQuery):
    telegram_id = int(callback.data.split(":")[1])
    user = users_service.get_user(telegram_id)

    if not user:
        await callback.answer("User not found", show_alert=True)
        return

    text = (
        "👤 <b>User card</b>\n\n"
        f"ID: <b>{user.telegram_id}</b>\n"
        f"Username: @{user.username or '-'}\n"
        f"Status: {'🟢 Active' if user.is_active else '🔴 Blocked'}"
    )

    await callback.message.edit_text(
        text,
        reply_markup=user_card_keyboard(user)
    )
    await callback.answer()


async def user_block_handler(callback: CallbackQuery):
    telegram_id = int(callback.data.split(":")[1])
    users_service.block_user(telegram_id)
    await user_open_handler(callback)


async def user_unblock_handler(callback: CallbackQuery):
    telegram_id = int(callback.data.split(":")[1])
    users_service.unblock_user(telegram_id)
    await user_open_handler(callback)


async def back_handler(callback: CallbackQuery):
    await callback.message.edit_text(
        "✅ <b>Admin panel</b>\n\nChoose a section:",
        reply_markup=main_menu_keyboard()
    )
    await callback.answer()


async def start_bot():
    bot = Bot(
        token=settings.admin_bot_token,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML
        )
    )

    dp = Dispatcher()

    dp.message.register(start_handler, CommandStart(), AdminOnlyFilter())

    dp.callback_query.register(
        menu_handler,
        lambda c: c.data.startswith("menu_"),
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

    await dp.start_polling(bot)
