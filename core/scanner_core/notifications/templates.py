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

    start_price = payload.get("start_price", "—")
    end_price = payload.get("end_price", "—")
    move_percent = payload.get("move_percent", "—")
    duration_candles = payload.get("duration_candles", "—")

    return (
        f"{event.symbol}\n\n"
        f"Статус: CORRECTION\n\n"
        f"Импульс:\n"
        f"Начало: {start_price}\n"
        f"Окончание: {end_price}\n"
        f"Движение: {move_percent}%\n"
        f"Длительность: {duration_candles} свечей\n\n"
        f"Сценарий активен. Идёт коррекция после импульса."
    )


TEMPLATES = {
    EventType.WATCHLIST_UPDATED: _format_watchlist,
    EventType.CORRECTION_STARTED: _format_correction,
}
