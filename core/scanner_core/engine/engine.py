from typing import Optional

from core.scanner_core.events import EventBus
from core.scanner_core.events.event_types import EventType
from core.scanner_core.state_machine import StateMachine, ScenarioState
from core.scanner_core.scenario import ScenarioManager
from core.scanner_core.market_context import MarketContextAnalyzer
from core.scanner_core.impulse import ImpulseDetector
from core.scanner_core.zones import ZoneDetector, ZoneManager

from .engine_result import EngineResult


class ScannerEngine:
    """
    Core orchestration engine.
    """

    def __init__(self) -> None:
        self._event_bus = EventBus()

        self._context_analyzer = MarketContextAnalyzer()
        self._impulse_detector = ImpulseDetector()
        self._zone_detector = ZoneDetector()

        self._scenario_manager = ScenarioManager()
        self._zone_managers: dict[str, ZoneManager] = {}

        self._market_context = None

    def run(
        self,
        symbol: str,
        market_data: dict,
        direction: str,
    ) -> Optional[EngineResult]:

        # ===============================
        # 1. MARKET CONTEXT
        # ===============================
        self._market_context = self._context_analyzer.analyze(
            market_data=market_data,
            event_bus=self._event_bus,
        )

        # ===============================
        # 2. SCENARIO
        # ===============================
        scenario = self._scenario_manager.get(symbol)
        state_before = scenario.state if scenario else ScenarioState.IDLE

        if scenario is None:
            scenario = self._scenario_manager.create(symbol, direction)
            self._zone_managers[symbol] = ZoneManager()

        zone_manager = self._zone_managers[symbol]

        # ===============================
        # 3. IMPULSE / CORRECTION
        # ===============================
        impulse = self._impulse_detector.analyze(
            symbol=symbol,
            market_data=market_data,
            direction=direction,
            market_context=self._market_context,
            event_bus=self._event_bus,
        )

        if impulse:
            scenario.impulse = impulse

        # ===============================
        # 4. APPLY EVENTS
        # ===============================
        state_changed = False
        events = self._event_bus.drain()

        for event in events:
            scenario.add_event(event)

            # 🔥 ZONES CREATED EXACTLY ON CORRECTION_STARTED
            if event.type == EventType.CORRECTION_STARTED:
                self._zone_detector.analyze(
                    symbol=symbol,
                    market_data=market_data,
                    zone_manager=zone_manager,
                    event_bus=self._event_bus,
                )

            new_state = StateMachine.transition(
                current_state=scenario.state,
                event_type=event.type,
            )

            if new_state:
                scenario.set_state(new_state)
                state_changed = True

        # ===============================
        # 5. CLEANUP
        # ===============================
        if scenario.state in (
            ScenarioState.CANCELLED,
            ScenarioState.COMPLETED,
        ):
            self._scenario_manager.remove(symbol)
            self._zone_managers.pop(symbol, None)

        # ===============================
        # 6. RESULT
        # ===============================
        return EngineResult(
            symbol=symbol,
            state=scenario.state,
            events=events,
            state_changed=(scenario.state != state_before) or state_changed,
        )
