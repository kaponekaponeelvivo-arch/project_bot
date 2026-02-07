from core.scanner_core.events.event_types import EventType


def _format_watchlist(event):
    """
    Aggregated watchlist message.
    Payload expected:
    {
        "items": [
            {"symbol": "BTCUSDT", "state": "trend_active"},
            ...
        ]
    }
    """
    items = event.payload.get("items", [])
    if not items:
        return None

    lines = ["📊 WATCHLIST:"]
    for item in items:
        lines.append(f"👀 {item['symbol']}: {item['state']}")

    return "\n".join(lines)


TEMPLATES = {

    # ===============================
    # SCENARIO
    # ===============================
    EventType.SCENARIO_STARTED: lambda e: (
        f"{e.symbol} — сценарий начат\n\n"
        f"Импульс зафиксирован\n"
        f"Контекст: тренд"
    ),

    EventType.CORRECTION_STARTED: lambda e: (
        f"{e.symbol} — коррекция\n\n"
        f"Импульс завершён\n"
        f"Ожидаем реакцию от зон"
    ),

    EventType.ZONE_REACTED: lambda e: (
        f"{e.symbol} — реакция от зоны\n\n"
        f"Статус: ожидаем подтверждение"
    ),

    EventType.SCENARIO_CONFIRMED: lambda e: (
        f"🟢 {e.symbol} — сценарий подтверждён\n\n"
        f"Статус: наблюдаем развитие"
    ),

    EventType.SCENARIO_COMPLETED: lambda e: (
        f"🟢 {e.symbol} — сценарий реализован\n\n"
        f"Движение: +{e.payload.get('move_percent', '?')}%\n"
        f"Сценарий завершён"
    ),

    EventType.SCENARIO_CANCELLED: lambda e: (
        f"🔴 {e.symbol} — сценарий отменён\n\n"
        f"Причина: {e.payload.get('reason', 'потеря структуры')}\n"
        f"Сценарий закрыт"
    ),

    # ===============================
    # WATCHLIST
    # ===============================
    EventType.WATCHLIST_UPDATED: _format_watchlist,
}
