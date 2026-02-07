from abc import ABC, abstractmethod
from core.scanner_core.events import Event


class Notifier(ABC):
    @abstractmethod
    def notify(self, event: Event) -> None:
        ...
