from typing import Dict, Optional

from core.scanner_core.events.event_bus import EventBus
from core.scanner_core.engine.engine_result import EngineResult

from core.scanner_core.market_context.analyzer import MarketContextAnalyzer
from core.scanner_core.impulse.impulse_detector import ImpulseDetector
from core.scanner_core.zones.zone_detector import ZoneDetector
from core.scanner_core.zones.zone_manager import ZoneManager
from core.scanner_core.reaction.reaction_detector import ReactionDetector
from core.scanner_core.tracking.tracking_service import TrackingService

from core.scanner_core.scenario import ScenarioManager
from core.scanner_core.scenario.scenario import Scenario
from core.scanner_core.state_machine import ScenarioState
from core.scanner_core.state_machine.state_machine import StateMachine


class ScannerEngine:
    def __init__(self) -> None:
        self._event_bus = EventBus()

        self._market_context = MarketContextAnalyzer()
        self._impulse_detector = ImpulseDetector()
        self._zone_detector = ZoneDetector()
        self._reaction_detector = ReactionDetector()
        self._tracking_service = TrackingService()

        self._scenario_manager = ScenarioManager()
        self._zone_manager = ZoneManager()

    def _resolve_direction(
        self,
        market_data: Dict,
        market_context,
    ) -> Optional[str]:

        trend = market_data.get("trend")
        if trend == "up":
            return "long"
        if trend == "down":
            return "short"

        if market_context == "TREND_UP":
            return "long"
        if market_context == "TREND_DOWN":
            return "short"

        return None

    def run(
        self,
        symbol: str,
        market_data: Dict,
    ) -> EngineResult:

        # ===============================
        # 1. MARKET CONTEXT
        # ===============================
        market_context = self._market_context.analyze(
            market_data=market_data,
            event_bus=self._event_bus,
        )

        direction = self._resolve_direction(market_data, market_context)

        scenario = self._scenario_manager.get(symbol)

        if direction is None:
            return EngineResult(
                symbol=symbol,
                state=scenario.state if scenario else ScenarioState.IDLE,
                state_changed=False,
                events=[],
            )

        # ===============================
        # 2. CREATE SCENARIO IF NEEDED
        # ===============================
        if scenario is None:
            scenario = self._scenario_manager.create(
                symbol=symbol,
                direction=direction,
            )

        # ===============================
        # 3. IMPULSE
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
                direction=direction,
                zone_manager=self._zone_manager,
                event_bus=self._event_bus,
            )

        # ===============================
        # 5. REACTION
        # ===============================
        if scenario.state == ScenarioState.CORRECTION:
            for zone in self._zone_manager.get_active_zones(symbol):
                self._reaction_detector.analyze(
                    symbol=symbol,
                    market_data=market_data,
                    zone=zone,
                    direction=direction,
                    event_bus=self._event_bus,
                )

        # ===============================
        # 6. APPLY STATE MACHINE
        # ===============================
        events = self._event_bus.drain()

        state_changed = False
        for event in events:
            new_state = StateMachine.transition(
                current_state=scenario.state,
                event_type=event.type,
            )
            if new_state and new_state != scenario.state:
                scenario.set_state(new_state)
                state_changed = True

            scenario.add_event(event)

        # ===============================
        # 7. TRACKING
        # ===============================
        if scenario.state == ScenarioState.CONFIRMED:
            if scenario.confirmed_price is not None:
                self._tracking_service.track(
                    symbol=symbol,
                    market_data=market_data,
                    confirmed_price=scenario.confirmed_price,
                    direction=direction,
                    event_bus=self._event_bus,
                )

        # ===============================
        # 8. RESULT
        # ===============================
        return EngineResult(
            symbol=symbol,
            state=scenario.state,
            state_changed=state_changed,
            events=events,
        )
