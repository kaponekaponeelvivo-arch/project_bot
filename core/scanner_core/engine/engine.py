from typing import Optional

from core.scanner_core.events import EventBus
from core.scanner_core.state_machine import StateMachine, ScenarioState
from core.scanner_core.scenario import ScenarioManager
from core.scanner_core.market_context import MarketContextAnalyzer
from core.scanner_core.impulse import ImpulseDetector
from core.scanner_core.zones import ZoneDetector, ZoneManager

from .engine_result import EngineResult


class ScannerEngine:
    """
    Core orchestration engine.
    Runs full analysis cycle for ONE symbol.
    """

    def __init__(self) -> None:
        self._event_bus = EventBus()

        self._context_analyzer = MarketContextAnalyzer()
        self._impulse_detector = ImpulseDetector()
        self._zone_detector = ZoneDetector()

        self._scenario_manager = ScenarioManager()
        self._zone_managers: dict[str, ZoneManager] = {}

    def run(
        self,
        symbol: str,
        market_data: dict,
        direction: str,
    ) -> Optional[EngineResult]:

        # ===============================
        # 1. Market context
        # ===============================
        self._context_analyzer.analyze(
            market_data=market_data,
            event_bus=self._event_bus,
        )

        # ===============================
        # 2. Scenario get / create
        # ===============================
        scenario = self._scenario_manager.get(symbol)
        state_before = scenario.state if scenario else ScenarioState.IDLE

        if scenario is None:
            scenario = self._scenario_manager.create(
                symbol=symbol,
                direction=direction,
            )
            self._zone_managers[symbol] = ZoneManager()

        zone_manager = self._zone_managers[symbol]

        # ===============================
        # 3. Impulse detection
        # ===============================
        impulse = self._impulse_detector.analyze(
            symbol=symbol,
            market_data=market_data,
            direction=direction,
            event_bus=self._event_bus,
        )
        if impulse:
            scenario.impulse = impulse

        # ===============================
        # 4. Zone detection
        #    ONLY IN CORRECTION
        # ===============================
        if scenario.state == ScenarioState.CORRECTION:
            self._zone_detector.analyze(
                symbol=symbol,
                market_data=market_data,
                zone_manager=zone_manager,
                event_bus=self._event_bus,
            )

        # ===============================
        # 5. Apply events
        # ===============================
        state_changed = False
        events = self._event_bus.drain()

        for event in events:
            scenario.add_event(event)

            new_state = StateMachine.transition(
                current_state=scenario.state,
                event_type=event.type,
            )

            if new_state:
                scenario.set_state(new_state)
                state_changed = True

        # ===============================
        # 6. Cleanup
        # ===============================
        if scenario.state in (ScenarioState.CANCELLED, ScenarioState.COMPLETED):
            self._scenario_manager.remove(symbol)
            self._zone_managers.pop(symbol, None)

        # ===============================
        # 7. Result
        # ===============================
        return EngineResult(
            symbol=symbol,
            state=scenario.state,
            events=events,
            state_changed=(scenario.state != state_before) or state_changed,
        )
