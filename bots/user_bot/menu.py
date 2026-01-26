from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu(has_subscription: bool) -> InlineKeyboardMarkup:
    buy_text = "🔄 Extend subscription" if has_subscription else "💳 Buy subscription"

    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 My subscription", callback_data="my_subscription")],
        [InlineKeyboardButton(text=buy_text, callback_data="buy_subscription")],
        [InlineKeyboardButton(text="📡 Screeners", callback_data="screeners")],
        [InlineKeyboardButton(text="🤖 About screener", callback_data="about")],
        [InlineKeyboardButton(text="🎯 Referral program", callback_data="referrals")],
        [InlineKeyboardButton(text="🆘 Support", callback_data="support")],
    ])


def plans_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="7 days", callback_data="plan_7"),
            InlineKeyboardButton(text="30 days", callback_data="plan_30"),
            InlineKeyboardButton(text="90 days", callback_data="plan_90"),
        ],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="back_main")],
    ])


def back_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back", callback_data="back_main")]
    ])
