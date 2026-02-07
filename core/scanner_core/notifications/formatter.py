from core.scanner_core.events import Event
from core.scanner_core.notifications.templates import TEMPLATES


class NotificationFormatter:
    """
    Converts Event → human-readable message.
    """

    @staticmethod
    def format(event: Event) -> str | None:
        template = TEMPLATES.get(event.type)
        if not template:
            return None

        return template(event)
