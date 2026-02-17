from core.scanner_core.events import Event
from core.scanner_core.events.event_types import EventType
from core.scanner_core.events.event_bus import EventBus

from core.scanner_core.state_machine import StateMachine
from core.scanner_core.state_machine.states import ScenarioState

from core.scanner_core.scenario.scenario_manager import ScenarioManager

from core.scanner_core.notifications.router import NotificationRouter
from core.scanner_core.notifications.console_notifier import ConsoleNotifier
from core.scanner_core.notifications.telegram_notifier import TelegramNotifier


class ScannerEngine:

    def __init__(self) -> None:
        self._event_bus = EventBus()
        self._scenario_manager = ScenarioManager()

        self._notifier = NotificationRouter(
            notifiers=[
                ConsoleNotifier(),
                TelegramNotifier(),
            ]
        )

    # ==========================================================

    def run(
        self,
        symbol: str,
        detected_event: EventType,
        payload: dict | None = None,
    ) -> None:

        scenario = self._scenario_manager.get(symbol)

        if not scenario:
            scenario = self._scenario_manager.create(
                symbol=symbol,
                direction="LONG",
            )

        event = Event(
            type=detected_event,
            symbol=symbol,
            payload=payload,
        )

        self._event_bus.publish(event)

        while self._event_bus.has_events():
            events = self._event_bus.drain()

            for event in events:
                self._apply_event(scenario, event)

        if scenario.state in (
            ScenarioState.COMPLETED,
            ScenarioState.CANCELLED,
        ):
            self._scenario_manager.remove(symbol)

    # ==========================================================

    def _apply_event(self, scenario, event: Event) -> None:

        if not StateMachine.can_transition(scenario.state, event.type):
            print(
                f"[FSM WARNING] invalid transition "
                f"{scenario.state} -> {event.type}"
            )
            return

        new_state = StateMachine.next_state(
            scenario.state,
            event.type,
        )

        if new_state:
            scenario.set_state(new_state)
            scenario.add_event(event)
            self._notifier.handle(event)
