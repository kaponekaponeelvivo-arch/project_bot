from core.scanner_core.events import Event
from core.scanner_core.events.event_types import EventType
from core.scanner_core.events.event_bus import EventBus

from core.scanner_core.state_machine import StateMachine
from core.scanner_core.state_machine.states import ScenarioState

from core.scanner_core.scenario.scenario_manager import ScenarioManager

from core.scanner_core.notifications.router import NotificationRouter
from core.scanner_core.notifications.console_notifier import ConsoleNotifier
from core.scanner_core.notifications.telegram_notifier import TelegramNotifier

from core.scanner_core.structure.structure_analyzer import StructureAnalyzer
from core.scanner_core.legacy.detectors.zone_detector import ZoneDetector
from core.scanner_core.legacy.detectors.reaction_detector import ReactionDetector
from core.scanner_core.legacy.detectors.confirmed_detector import ConfirmedDetector
from core.scanner_core.reaction.completed_detector import CompletedDetector


class ScannerEngine:

    def __init__(self) -> None:
        self._event_bus = EventBus()
        self._scenario_manager = ScenarioManager()

        self._structure = StructureAnalyzer()
        self._zone_detector = ZoneDetector()
        self._reaction_detector = ReactionDetector()
        self._confirmed_detector = ConfirmedDetector()
        self._completed_detector = CompletedDetector()

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
        market_data: dict,     # 5M
        reaction_data: dict,   # 15M
        impulse_data: dict,    # 1H
        context_data: dict,    # 4H
    ) -> None:

        scenario = self._scenario_manager.get(symbol)

        if not scenario:
            scenario = self._scenario_manager.create(
                symbol=symbol,
                direction="LONG",
            )

        # ======================================================
        # 1️⃣ STRUCTURE
        # ======================================================

        structure = self._structure.analyze(
            symbol=symbol,
            market_data=market_data,
            impulse_data=impulse_data,
            context_data=context_data,
            market_context=None,
        )

        if structure and structure.get("phase"):
            phase = structure["phase"]
            payload = structure.get("payload", {})

            self._event_bus.publish(
                Event(
                    type=self._map_phase_to_event(phase),
                    symbol=symbol,
                    payload=payload,
                )
            )

        self._drain_and_apply(scenario)

        # ======================================================
        # 2️⃣ ZONE (FVG / FIB)
        # ======================================================

        self._zone_detector.analyze(
            symbol=symbol,
            impulse_data=impulse_data,
            scenario=scenario,
            event_bus=self._event_bus,
        )

        self._drain_and_apply(scenario)

        # ======================================================
        # 3️⃣ REACTION (15M)
        # ======================================================

        self._reaction_detector.analyze(
            symbol=symbol,
            reaction_data=reaction_data,
            scenario=scenario,
            event_bus=self._event_bus,
        )

        self._drain_and_apply(scenario)

        # ======================================================
        # 4️⃣ CONFIRMATION (5M)
        # ======================================================

        self._confirmed_detector.analyze(
            symbol=symbol,
            market_data=market_data,
            scenario=scenario,
            event_bus=self._event_bus,
        )

        self._drain_and_apply(scenario)

        # ======================================================
        # 5️⃣ COMPLETION (TP2 / STOP)
        # ======================================================

        self._completed_detector.analyze(
            symbol=symbol,
            market_data=market_data,
            scenario=scenario,
            event_bus=self._event_bus,
        )

        self._drain_and_apply(scenario)

        # ======================================================
        # TERMINAL CLEANUP
        # ======================================================

        if scenario.state in (
            ScenarioState.COMPLETED,
            ScenarioState.CANCELLED,
        ):
            self._scenario_manager.remove(symbol)

    # ==========================================================

    def _drain_and_apply(self, scenario) -> None:
        """
        Apply all queued events immediately.
        Ensures next detector sees updated scenario.state.
        """
        while self._event_bus.has_events():
            events = self._event_bus.drain()

            for event in events:
                self._apply_event(scenario, event)

    # ==========================================================

    def _map_phase_to_event(self, phase: ScenarioState) -> EventType:

        mapping = {
            ScenarioState.TREND_ACTIVE: EventType.MARKET_CONTEXT_CHANGED,
            ScenarioState.IMPULSE: EventType.IMPULSE_DETECTED,
            ScenarioState.CORRECTION: EventType.CORRECTION_STARTED,
            ScenarioState.CANCELLED: EventType.SCENARIO_CANCELLED,
        }

        return mapping.get(phase, EventType.MARKET_CONTEXT_CHANGED)

    # ==========================================================

    def _apply_event(self, scenario, event: Event) -> None:

        if not StateMachine.can_transition(scenario.state, event.type):
            return

        new_state = StateMachine.next_state(
            scenario.state,
            event.type,
        )

        if new_state:
            scenario.set_state(new_state)
            scenario.add_event(event)
            self._notifier.handle(event)
