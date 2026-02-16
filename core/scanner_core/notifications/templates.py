from core.scanner_core.events import Event
from core.scanner_core.events.event_types import EventType


def _format_watchlist(event):
    try:
        snapshot = event.payload["snapshot"]
    except KeyError:
        return None

    if not snapshot:
        return None

    lines = ["📊 Watchlist"]
    block_order = ["CONFIRMED", "REACTION", "CORRECTION"]

    for block_name in block_order:
        symbols = []

        for priority, tickers in snapshot.items():
            if getattr(priority, "name", None) == block_name:
                symbols = tickers
                break

        if not symbols:
            continue

        lines.append(f"\n{block_name}:")
        for ticker in symbols:
            lines.append(str(ticker))

    if len(lines) == 1:
        return None

    return "\n".join(lines)


def _format_correction(event: Event) -> str:
    payload = event.payload or {}

    return (
        f"{event.symbol}\n\n"
        f"Статус: CORRECTION\n\n"
        f"Импульс:\n"
        f"Начало: {payload.get('start_price', '—')}\n"
        f"Окончание: {payload.get('end_price', '—')}\n"
        f"Движение: {payload.get('move_percent', '—')}%\n"
        f"Длительность: {payload.get('duration_candles', '—')} свечей\n\n"
        f"Сценарий активен. Идёт коррекция после импульса."
    )


def _format_reaction(event: Event) -> str:
    payload = event.payload or {}

    return (
        f"{event.symbol}\n\n"
        f"Статус: REACTION\n\n"
        f"Зона: {payload.get('zone_type', '—')}\n"
        f"Диапазон: {payload.get('price_from', '—')} – {payload.get('price_to', '—')}\n"
        f"Глубина коррекции: {payload.get('correction_depth_pct', '—')}%\n\n"
        f"Цена вошла в потенциальную зону реакции."
    )


def _format_confirmed(event: Event) -> str:
    return (
        f"{event.symbol}\n\n"
        f"Статус: CONFIRMED\n\n"
        f"Сценарий подтверждён.\n"
        f"Структура сломана в сторону тренда."
    )


TEMPLATES = {
    EventType.WATCHLIST_UPDATED: _format_watchlist,
    EventType.CORRECTION_STARTED: _format_correction,
    EventType.ZONE_REACTED: _format_reaction,
    EventType.SCENARIO_CONFIRMED: _format_confirmed,
}
