from core.scanner_core.events import Event
from core.scanner_core.notifications.formatter import NotificationFormatter


class ConsoleNotifier:
    """
    Prints notifications to console (dev/debug).
    """

    def handle(self, event: Event) -> None:
        message = NotificationFormatter.format(event)
        if not message:
            return

        print(f"[NOTIFY] {event.type.value} | {event.symbol}")
