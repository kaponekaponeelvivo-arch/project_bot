from typing import Dict

from core.scanner_core.events import EventType
from core.scanner_core.events.event_bus import EventBus

from core.scanner_core.market_context.analyzer import MarketContextAnalyzer
from core.scanner_core.impulse.impulse_detector import ImpulseDetector
from core.scanner_core.zones.zone_detector import ZoneDetector
from core.scanner_core.zones.zone_manager import ZoneManager
from core.scanner_core.reaction.reaction_detector import ReactionDetector
from core.scanner_core.reaction.confirmed_detector import ConfirmedDetector
from core.scanner_core.tracking.tracking_service import TrackingService

from core.scanner_core.scenario.scenario_manager import ScenarioManager
from core.scanner_core.state_machine import ScenarioState, StateMachine


class ScannerEngine:
    """
    Central orchestrator of scanner_core.
    """

    def __init__(self) -> None:
        self._event_bus = EventBus()

        self._market_context = MarketContextAnalyzer()
        self._impulse_detector = ImpulseDetector()
        self._zone_detector = ZoneDetector()
        self._zone_manager = ZoneManager()
        self._reaction_detector = ReactionDetector()
        self._confirmed_detector = ConfirmedDetector()
        self._tracking_service = TrackingService()

        self._scenario_manager = ScenarioManager()

    def run(self, symbol: str, market_data: dict) -> Dict:
        """
        Single engine cycle.
        """

        # ===============================
        # 1. MARKET CONTEXT
        # ===============================
        market_context = self._market_context.analyze(
            market_data=market_data,
            event_bus=self._event_bus,
        )

        # ===============================
        # 2. SCENARIO INIT
        # ===============================
        scenario = self._scenario_manager.get(symbol)
        if scenario is None:
            scenario = self._scenario_manager.create(
                symbol=symbol,
                direction="LONG",  # direction is fixed by context later
            )

        # ===============================
        # 3. IMPULSE
        # ===============================
        impulse = self._impulse_detector.analyze(
            symbol=symbol,
            market_data=market_data,
            direction=scenario.direction,
            market_context=market_context,
            event_bus=self._event_bus,
        )

        # ===============================
        # 4. ZONES (ONLY IN CORRECTION)
        # ===============================
        if scenario.state == ScenarioState.CORRECTION:
            self._zone_detector.analyze(
                symbol=symbol,
                market_data=market_data,
                direction=scenario.direction,
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
                    direction=scenario.direction,
                    event_bus=self._event_bus,
                )

        # ===============================
        # 6. CONFIRMED
        # ===============================
        if scenario.state == ScenarioState.REACTION:
            self._confirmed_detector.analyze(
                symbol=symbol,
                market_data=market_data,
                direction=scenario.direction,
                market_context=market_context,
                event_bus=self._event_bus,
            )

        # ===============================
        # 7. FSM TRANSITIONS
        # ===============================
        state_changed = False
        for event in self._event_bus.drain():
            scenario.add_event(event)

            next_state = StateMachine.transition(
                current_state=scenario.state,
                event_type=event.type,
            )

            if next_state:
                scenario.set_state(next_state)
                state_changed = True

                if event.type == EventType.SCENARIO_CONFIRMED:
                    price = market_data.get("price")
                    if price:
                        self._tracking_service.start(price)

                if event.type in (
                    EventType.SCENARIO_COMPLETED,
                    EventType.SCENARIO_CANCELLED,
                ):
                    self._tracking_service.reset()
                    self._scenario_manager.remove(symbol)

        # ===============================
        # 8. TRACKING
        # ===============================
        if scenario.state == ScenarioState.CONFIRMED:
            self._tracking_service.track(
                symbol=symbol,
                market_data=market_data,
                direction=scenario.direction,
                event_bus=self._event_bus,
            )

        return {
            "symbol": symbol,
            "state": scenario.state.value,
            "state_changed": state_changed,
            "events": [e.type.value for e in scenario.events[-5:]],
        }
