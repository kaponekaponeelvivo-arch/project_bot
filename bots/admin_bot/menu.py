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


def users_list_keyboard(users):
    buttons = [
        [InlineKeyboardButton(
            text=f"{'🟢' if u.is_active else '🔴'} {u.telegram_id}",
            callback_data=f"user_open:{u.telegram_id}"
        )]
        for u in users
    ]
    buttons.append(
        [InlineKeyboardButton(text="⬅️ Back", callback_data="menu_back")]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def user_card_keyboard(user):
    buttons = [
        [
            InlineKeyboardButton(text="➕ +7 days", callback_data=f"user_sub_add:7:{user.telegram_id}"),
            InlineKeyboardButton(text="➕ +30 days", callback_data=f"user_sub_add:30:{user.telegram_id}"),
        ],
        [
            InlineKeyboardButton(text="❌ Remove subscription", callback_data=f"user_sub_remove:{user.telegram_id}")
        ],
    ]

    if user.is_active:
        buttons.append(
            [InlineKeyboardButton(text="🔒 Block", callback_data=f"user_block:{user.telegram_id}")]
        )
    else:
        buttons.append(
            [InlineKeyboardButton(text="🔓 Unblock", callback_data=f"user_unblock:{user.telegram_id}")]
        )

    buttons.append(
        [InlineKeyboardButton(text="⬅️ Back", callback_data="menu_users")]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)
