from core.scanner_core.events.event_bus import EventBus
from core.scanner_core.market_context.analyzer import MarketContextAnalyzer
from core.scanner_core.impulse.impulse_detector import ImpulseDetector
from core.scanner_core.zones.zone_detector import ZoneDetector
from core.scanner_core.zones.zone_manager import ZoneManager
from core.scanner_core.reaction.reaction_detector import ReactionDetector
from core.scanner_core.reaction.confirmed_detector import ConfirmedDetector
from core.scanner_core.scenario.scenario_manager import ScenarioManager
from core.scanner_core.state_machine.state_machine import StateMachine
from core.scanner_core.state_machine.states import ScenarioState


class ScannerEngine:
    """
    Core orchestrator.
    """

    def __init__(self) -> None:
        self._event_bus = EventBus()

        self._market_context = MarketContextAnalyzer()
        self._impulse_detector = ImpulseDetector()
        self._zone_detector = ZoneDetector()
        self._reaction_detector = ReactionDetector()
        self._confirmed_detector = ConfirmedDetector()

        self._scenario_manager = ScenarioManager()
        self._zone_manager = ZoneManager()

    def run(self, symbol: str, market_data: dict) -> dict:
        # ===============================
        # 1. MARKET CONTEXT
        # ===============================
        market_context = self._market_context.analyze(
            market_data=market_data,
            event_bus=self._event_bus,
        )

        # ===============================
        # 2. SCENARIO
        # ===============================
        scenario = self._scenario_manager.get(symbol)
        if scenario is None:
            # направление фиксируется один раз
            direction = (
                "LONG"
                if market_context.phase.value == "trend_up"
                else "SHORT"
            )
            scenario = self._scenario_manager.create(symbol, direction)

        direction = scenario.direction

        # ===============================
        # 3. IMPULSE / CORRECTION
        # ===============================
        self._impulse_detector.analyze(
            symbol=symbol,
            market_data=market_data,
            direction=direction,
            market_context=market_context,
            event_bus=self._event_bus,
        )

        # ===============================
        # 4. ZONES
        # ===============================
        if scenario.state == ScenarioState.CORRECTION:
            self._zone_detector.analyze(
                symbol=symbol,
                market_data=market_data,
                event_bus=self._event_bus,
                zone_manager=self._zone_manager,
            )

        # ===============================
        # 5. REACTION
        # ===============================
        if scenario.state == ScenarioState.CORRECTION:
            for zone in self._zone_manager.get_active_zones():
                self._reaction_detector.analyze(
                    symbol=symbol,
                    market_data=market_data,
                    zone=zone,
                    direction=direction,
                    event_bus=self._event_bus,
                )

        # ===============================
        # 6. CONFIRMED
        # ===============================
        if scenario.state == ScenarioState.REACTION:
            self._confirmed_detector.analyze(
                symbol=symbol,
                market_data=market_data,
                direction=direction,
                event_bus=self._event_bus,
            )

        # ===============================
        # 7. APPLY EVENTS (FSM)
        # ===============================
        events = self._event_bus.drain()
        state_changed = False

        for event in events:
            scenario.add_event(event)

            new_state = StateMachine.transition(
                scenario.state,
                event.type,
            )

            if new_state:
                scenario.set_state(new_state)
                state_changed = True

        return {
            "symbol": symbol,
            "state": scenario.state.value,
            "state_changed": state_changed,
            "events": [e.type.value for e in events],
        }
