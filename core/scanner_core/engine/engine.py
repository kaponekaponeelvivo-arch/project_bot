from core.scanner_core.events import Event, EventType
from core.scanner_core.events.event_bus import EventBus

from core.scanner_core.market_context.analyzer import MarketContextAnalyzer
from core.scanner_core.impulse.impulse_detector import ImpulseDetector
from core.scanner_core.zones.zone_detector import ZoneDetector
from core.scanner_core.zones.zone_manager import ZoneManager
from core.scanner_core.reaction.reaction_detector import ReactionDetector
from core.scanner_core.reaction.confirmed_detector import ConfirmedDetector

from core.scanner_core.scenario.scenario_manager import ScenarioManager
from core.scanner_core.state_machine import StateMachine, ScenarioState


class ScannerEngine:
    """
    Core orchestrator.
    Executes detectors and applies FSM transitions.
    """

    def __init__(self) -> None:
        self._event_bus = EventBus()

        self._market_context = MarketContextAnalyzer()
        self._impulse_detector = ImpulseDetector()
        self._zone_detector = ZoneDetector()
        self._zone_manager = ZoneManager()
        self._reaction_detector = ReactionDetector()
        self._confirmed_detector = ConfirmedDetector()

        self._scenario_manager = ScenarioManager()

    def run(self, symbol: str, market_data: dict) -> dict:
        """
        One engine cycle for one symbol.
        """

        # ===============================
        # 1️⃣ Market context
        # ===============================
        market_context = self._market_context.analyze(
            market_data=market_data,
            event_bus=self._event_bus,
        )

        # ===============================
        # 2️⃣ Get or create scenario
        # ===============================
        scenario = self._scenario_manager.get(symbol)
        if scenario is None:
            scenario = self._scenario_manager.create(
                symbol=symbol,
                direction="LONG",  # direction is abstract here, not entry signal
            )

        # ===============================
        # 3️⃣ Impulse detection
        # ===============================
        impulse = self._impulse_detector.analyze(
            symbol=symbol,
            market_data=market_data,
            direction=scenario.direction,
            market_context=market_context.phase.value,
            event_bus=self._event_bus,
        )

        # ⚠️ IMPORTANT:
        # Impulse itself does NOT start scenario.
        # Scenario starts ONLY if market context is TREND.
        if impulse and market_context.phase.value.startswith("TREND"):
            self._event_bus.publish(
                Event(
                    type=EventType.SCENARIO_STARTED,
                    symbol=symbol,
                )
            )

        # ===============================
        # 4️⃣ Zones (only in CORRECTION)
        # ===============================
        if scenario.state == ScenarioState.CORRECTION:
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
                    direction=scenario.direction,
                    event_bus=self._event_bus,
                )

        # ===============================
        # 5️⃣ CONFIRMED
        # ===============================
        if scenario.state == ScenarioState.REACTION:
            self._confirmed_detector.analyze(
                symbol=symbol,
                market_data=market_data,
                direction=scenario.direction,
                market_context=market_context.phase.value,
                event_bus=self._event_bus,
            )

        # ===============================
        # 6️⃣ Apply FSM transitions
        # ===============================
        events = self._event_bus.drain()
        state_changed = False

        for event in events:
            next_state = StateMachine.transition(
                current_state=scenario.state,
                event_type=event.type,
            )

            if next_state:
                scenario.set_state(next_state)
                state_changed = True

            scenario.add_event(event)

        return {
            "symbol": symbol,
            "state": scenario.state.value,
            "state_changed": state_changed,
            "events": events,
        }
