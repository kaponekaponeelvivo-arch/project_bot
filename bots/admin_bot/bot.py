from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, BaseFilter
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config.settings import settings
from bots.admin_bot.menu import main_menu_keyboard, back_keyboard


class AdminOnlyFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id == settings.admin_telegram_id


class AdminOnlyCallbackFilter(BaseFilter):
    async def __call__(self, callback: CallbackQuery) -> bool:
        return callback.from_user.id == settings.admin_telegram_id


async def start_handler(message: Message):
    await message.answer(
        "✅ <b>Admin panel</b>\n\n"
        "Choose a section:",
        reply_markup=main_menu_keyboard()
    )


async def menu_handler(callback: CallbackQuery):
    section = callback.data.replace("menu_", "")

    texts = {
        "users": "📊 <b>Users</b>\n\nВ разработке.",
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

    dp.message.register(
        start_handler,
        CommandStart(),
        AdminOnlyFilter()
    )

    dp.callback_query.register(
        menu_handler,
        lambda c: c.data.startswith("menu_") and c.data != "menu_back",
        AdminOnlyCallbackFilter()
    )

    dp.callback_query.register(
        back_handler,
        lambda c: c.data == "menu_back",
        AdminOnlyCallbackFilter()
    )

    await dp.start_polling(bot)
