from core.scanner_core.events import Event, EventType
from core.scanner_core.events.event_bus import EventBus

from core.scanner_core.market_context.analyzer import MarketContextAnalyzer
from core.scanner_core.state_machine import StateMachine, ScenarioState

from core.scanner_core.scenario.scenario_manager import ScenarioManager
from core.scanner_core.watchlist.watchlist import Watchlist

from core.scanner_core.notifications.router import NotificationRouter
from core.scanner_core.notifications.console_notifier import ConsoleNotifier
from core.scanner_core.notifications.telegram_notifier import TelegramNotifier

from core.scanner_core.structure.structure_analyzer import StructureAnalyzer
from core.scanner_core.zones.zone_manager import ZoneManager
from core.scanner_core.legacy.detectors.zone_detector import ZoneDetector
from core.scanner_core.legacy.detectors.reaction_detector import ReactionDetector
from core.scanner_core.legacy.detectors.confirmed_detector import ConfirmedDetector


class ScannerEngine:

    def __init__(self) -> None:
        self._event_bus = EventBus()

        self._market_context = MarketContextAnalyzer()
        self._structure = StructureAnalyzer()

        self._zone_manager = ZoneManager()
        self._zone_detector = ZoneDetector()
        self._reaction_detector = ReactionDetector()
        self._confirmed_detector = ConfirmedDetector()

        self._scenario_manager = ScenarioManager()
        self._watchlist = Watchlist()

        self._notifier = NotificationRouter(
            notifiers=[
                ConsoleNotifier(),
                TelegramNotifier(),
            ]
        )

        # 🔥 Храним payload по символу
        self._last_payloads = {}

    # ==========================================================
    def run(
        self,
        symbol: str,
        market_data: dict,
        impulse_data: dict,
        context_data: dict,
    ) -> dict:

        # CONTEXT
        market_context = self._market_context.analyze(
            market_data=context_data,
            event_bus=self._event_bus,
        )

        # STRUCTURE
        structure = self._structure.analyze(
            symbol=symbol,
            market_data=market_data,
            impulse_data=impulse_data,
            context_data=context_data,
            market_context=market_context,
        )

        direction = structure.get("direction")
        target_state = structure.get("phase")
        payload = structure.get("payload", {})

        scenario = self._scenario_manager.get(symbol)

        # ❌ Потеря структуры
        if not direction or not target_state:

            if scenario:
                self._event_bus.publish(
                    Event(
                        type=EventType.SCENARIO_CANCELLED,
                        symbol=symbol,
                        payload=self._last_payloads.get(symbol),
                    )
                )

                self._scenario_manager.remove(symbol)
                self._watchlist.remove(symbol)
                self._zone_manager.clear()

            return

        # CREATE
        if scenario is None:
            scenario = self._scenario_manager.create(
                symbol=symbol,
                direction=direction,
            )

        if scenario.direction != direction:
            self._scenario_manager.remove(symbol)
            scenario = self._scenario_manager.create(
                symbol=symbol,
                direction=direction,
            )

        # 🔥 сохраняем payload
        self._last_payloads[symbol] = payload

        # STATE SYNC
        if scenario.state != target_state:

            if StateMachine.is_valid(target_state):

                scenario.set_state(target_state)

                event_type = self._map_state_to_event(target_state)

                if event_type:
                    self._event_bus.publish(
                        Event(
                            type=event_type,
                            symbol=symbol,
                            payload=payload,
                        )
                    )

        # DETECTORS
        self._zone_detector.analyze(
            symbol=symbol,
            market_data=market_data,
            scenario=scenario,
            zone_manager=self._zone_manager,
            event_bus=self._event_bus,
        )

        for zone in self._zone_manager.get_active_zones():
            self._reaction_detector.analyze(
                symbol=symbol,
                market_data=market_data,
                zone=zone,
                direction=direction,
                event_bus=self._event_bus,
            )

        self._confirmed_detector.analyze(
            symbol=symbol,
            market_data=market_data,
            direction=direction,
            market_context=market_context,
            event_bus=self._event_bus,
        )

        # APPLY EVENTS
        events = self._event_bus.drain()

        for event in events:

            # 🔥 если нет payload — приклеиваем последний
            if not event.payload:
                event.payload = self._last_payloads.get(symbol)

            new_state = self._map_event_to_state(event.type)

            if new_state and StateMachine.is_valid(new_state):

                # блок повторного confirmed
                if (
                    new_state == ScenarioState.CONFIRMED
                    and scenario.state == ScenarioState.CONFIRMED
                ):
                    continue

                scenario.set_state(new_state)

            self._notifier.handle(event)
            scenario.add_event(event)

        # WATCHLIST
        if scenario.state not in (
            ScenarioState.CANCELLED,
            ScenarioState.COMPLETED,
        ):
            self._watchlist.update(symbol, scenario.state)

        self._watchlist.emit(self._event_bus)

        watchlist_events = self._event_bus.drain()
        for event in watchlist_events:
            self._notifier.handle(event)

    # ==========================================================
    def _map_state_to_event(self, state: ScenarioState):

        mapping = {
            ScenarioState.IMPULSE: EventType.IMPULSE_DETECTED,
            ScenarioState.CORRECTION: EventType.CORRECTION_STARTED,
        }

        return mapping.get(state)

    # ==========================================================
    def _map_event_to_state(self, event_type: EventType):

        mapping = {
            EventType.ZONE_REACTED: ScenarioState.REACTION,
            EventType.SCENARIO_CONFIRMED: ScenarioState.CONFIRMED,
            EventType.SCENARIO_CANCELLED: ScenarioState.CANCELLED,
        }

        return mapping.get(event_type)
