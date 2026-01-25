from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 Users", callback_data="menu_users"),
            InlineKeyboardButton(text="💳 Subscriptions", callback_data="menu_subscriptions"),
        ],
        [
            InlineKeyboardButton(text="🤖 Screeners", callback_data="menu_screeners"),
            InlineKeyboardButton(text="🎯 Referrals", callback_data="menu_referrals"),
        ],
        [
            InlineKeyboardButton(text="📈 Stats", callback_data="menu_stats"),
            InlineKeyboardButton(text="⚙️ System", callback_data="menu_system"),
        ],
    ])


def back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back", callback_data="menu_back")]
    ])
