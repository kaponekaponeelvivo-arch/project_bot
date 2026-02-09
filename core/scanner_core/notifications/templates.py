from core.scanner_core.events.event_types import EventType


PRIORITY_EMOJI = {
    "TREND_ACTIVE": "👀",
    "IMPULSE": "⚡",
    "CORRECTION": "🔄",
    "REACTION": "🎯",
    "CONFIRMED": "🟢",
}


def _format_watchlist(event):
    snapshot = event.payload.get("snapshot", {})
    if not snapshot:
        return None

    lines = ["📊 <b>WATCHLIST</b>"]

    for priority, symbols in snapshot.items():
        name = priority.name
        emoji = PRIORITY_EMOJI.get(name, "•")
        lines.append(f"\n{emoji} <b>{name}</b>:")

        for s in symbols:
            lines.append(f"  • {s}")

    return "\n".join(lines)


TEMPLATES = {
    EventType.WATCHLIST_UPDATED: _format_watchlist,
}
