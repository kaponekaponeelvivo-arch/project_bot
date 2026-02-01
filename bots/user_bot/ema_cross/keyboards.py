from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def ema_cross_main_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⚙️ Настройка", callback_data="ema:settings")],
            [InlineKeyboardButton(text="👤 Личный кабинет", callback_data="ema:profile")],
            [InlineKeyboardButton(text="ℹ️ Инфо", callback_data="ema:info")],
        ]
    )


def ema_settings_kb(enabled: bool) -> InlineKeyboardMarkup:
    toggle_text = "🔌 Выключить" if enabled else "🔌 Включить"

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=toggle_text, callback_data="ema:toggle")],
            [InlineKeyboardButton(text="⏱ Таймфрейм", callback_data="ema:timeframe")],
            [InlineKeyboardButton(text="📐 Тип пересечения", callback_data="ema:modes")],
            [InlineKeyboardButton(text="🌍 Market Filter", callback_data="ema:market")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="ema:back")],
        ]
    )


def ema_timeframe_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="15m", callback_data="ema:tf:15m"),
                InlineKeyboardButton(text="1H", callback_data="ema:tf:1h"),
            ],
            [
                InlineKeyboardButton(text="4H", callback_data="ema:tf:4h"),
                InlineKeyboardButton(text="1D", callback_data="ema:tf:1d"),
            ],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="ema:settings")],
        ]
    )


def ema_modes_kb(active_modes: list[str]) -> InlineKeyboardMarkup:
    def btn(label: str, code: str) -> InlineKeyboardButton:
        mark = "✅ " if code in active_modes else ""
        return InlineKeyboardButton(
            text=f"{mark}{label}",
            callback_data=f"ema:mode:{code}",
        )

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [btn("EMA 50 / 200", "ema_50_200")],
            [btn("EMA 21 / 50", "ema_21_50")],
            [btn("EMA 9 / 21", "ema_9_21")],
            [btn("EMA Cluster 9 / 21 / 50", "ema_cluster_9_21_50")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="ema:settings")],
        ]
    )
