from aiogram import Router, F
from aiogram.types import CallbackQuery

from core.services.ema_cross_settings import EmaCrossSettingsService
from bots.user_bot.ema_cross.keyboards import (
    ema_cross_main_kb,
    ema_settings_kb,
    ema_timeframe_kb,
    ema_modes_kb,
)

router = Router()


def render_status(settings) -> str:
    tf = settings.timeframe or "—"
    modes = "\n".join(f"• {m}" for m in settings.modes) or "—"

    return (
        "📊 EMA Cross\n\n"
        f"Статус: {'ON' if settings.enabled else 'OFF'}\n"
        f"TF: {tf}\n"
        f"Режимы:\n{modes}"
    )


@router.callback_query(F.data == "ema:open")
async def ema_open(
    call: CallbackQuery,
    service: EmaCrossSettingsService,
):
    settings = await service.get_settings(call.from_user.id)

    await call.message.edit_text(
        render_status(settings),
        reply_markup=ema_cross_main_kb(),
    )


@router.callback_query(F.data == "ema:settings")
async def ema_settings(
    call: CallbackQuery,
    service: EmaCrossSettingsService,
):
    settings = await service.get_settings(call.from_user.id)

    await call.message.edit_text(
        render_status(settings),
        reply_markup=ema_settings_kb(settings.enabled),
    )


@router.callback_query(F.data == "ema:toggle")
async def ema_toggle(
    call: CallbackQuery,
    service: EmaCrossSettingsService,
):
    settings = await service.get_settings(call.from_user.id)

    if settings.enabled:
        await service.disable(call.from_user.id)
    else:
        await service.enable(call.from_user.id)

    await ema_settings(call, service)


@router.callback_query(F.data == "ema:timeframe")
async def ema_timeframe(call: CallbackQuery):
    await call.message.edit_text(
        "⏱ Выберите таймфрейм",
        reply_markup=ema_timeframe_kb(),
    )


@router.callback_query(F.data.startswith("ema:tf:"))
async def ema_set_timeframe(
    call: CallbackQuery,
    service: EmaCrossSettingsService,
):
    tf = call.data.split(":")[-1]
    await service.set_timeframe(call.from_user.id, tf)
    await ema_settings(call, service)


@router.callback_query(F.data == "ema:modes")
async def ema_modes(
    call: CallbackQuery,
    service: EmaCrossSettingsService,
):
    settings = await service.get_settings(call.from_user.id)

    await call.message.edit_text(
        "📐 Выберите типы пересечений (макс. 2)",
        reply_markup=ema_modes_kb(settings.modes),
    )


@router.callback_query(F.data.startswith("ema:mode:"))
async def ema_toggle_mode(
    call: CallbackQuery,
    service: EmaCrossSettingsService,
):
    mode = call.data.split(":")[-1]

    try:
        settings = await service.get_settings(call.from_user.id)

        if mode in settings.modes:
            await service.remove_mode(call.from_user.id, mode)
        else:
            await service.add_mode(call.from_user.id, mode)

        await ema_modes(call, service)

    except ValueError:
        await call.answer(
            "Можно выбрать не более 2 режимов",
            show_alert=True,
        )


@router.callback_query(F.data == "ema:back")
async def ema_back(
    call: CallbackQuery,
    service: EmaCrossSettingsService,
):
    await ema_open(call, service)
