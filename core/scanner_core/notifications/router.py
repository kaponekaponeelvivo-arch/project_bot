from core.scanner_core.events import Event


class NotificationRouter:
    """
    Routes events to all registered notifiers.
    """

    def __init__(self, notifiers: list) -> None:
        self._notifiers = notifiers

    def handle(self, event: Event) -> None:
        for notifier in self._notifiers:
            notifier.handle(event)
