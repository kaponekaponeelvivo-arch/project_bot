from core.scanner_core.events import Event, EventType
from core.scanner_core.events.event_bus import EventBus

from core.scanner_core.market_context.analyzer import MarketContextAnalyzer
from core.scanner_core.impulse.impulse_detector import ImpulseDetector
from core.scanner_core.zones.zone_detector import ZoneDetector
from core.scanner_core.zones.zone_manager import ZoneManager
from core.scanner_core.reaction.reaction_detector import ReactionDetector
from core.scanner_core.reaction.confirmed_detector import ConfirmedDetector
from core.scanner_core.tracking.tracking_service import TrackingService

from core.scanner_core.scenario.scenario_manager import ScenarioManager
from core.scanner_core.state_machine import StateMachine, ScenarioState

from core.scanner_core.notifications.router import NotificationRouter
from core.scanner_core.notifications.console_notifier import ConsoleNotifier
from core.scanner_core.notifications.telegram_notifier import TelegramNotifier

from core.scanner_core.watchlist.watchlist import Watchlist


class ScannerEngine:
    """
    Core orchestrator.
    Executes detectors, FSM transitions and updates Watchlist.
    """

    def __init__(self) -> None:
        self._event_bus = EventBus()

        # Core analyzers
        self._market_context = MarketContextAnalyzer()
        self._impulse_detectors: dict[str, ImpulseDetector] = {}
        self._zone_detector = ZoneDetector()
        self._zone_manager = ZoneManager()
        self._reaction_detector = ReactionDetector()
        self._confirmed_detector = ConfirmedDetector()
        self._tracking = TrackingService()

        # Scenario & watchlist
        self._scenario_manager = ScenarioManager()
        self._watchlist = Watchlist()

        # 🔔 Notifications (DEV + SCANNER BOT)
        self._notifier = NotificationRouter(
            notifiers=[
                ConsoleNotifier(),
                TelegramNotifier(),
            ]
        )

    def _process_event(
        self,
        event: Event,
        scenario,
        market_data: dict,
        events,
        event_index: int,
        symbol: str,
        ux_event_types,
        emit_watchlist: bool,
    ) -> bool:
        if event.type == EventType.IMPULSE_DETECTED:
            scenario.last_impulse = dict(event.payload or {})

        if event.type == EventType.CORRECTION_STARTED and scenario.last_impulse:
            event.payload["start_price"] = scenario.last_impulse.get("start_price")
            event.payload["end_price"] = scenario.last_impulse.get("end_price")
            event.payload["move_percent"] = scenario.last_impulse.get("move_percent")
            event.payload["duration_candles"] = scenario.last_impulse.get("duration_candles")

        # 🔔 notify (console + telegram)
        self._notifier.handle(event)

        state_changed = False
        next_state = StateMachine.transition(
            current_state=scenario.state,
            event_type=event.type,
        )

        if next_state:
            scenario.set_state(next_state)
            state_changed = True

            # ▶ start tracking
            if next_state == ScenarioState.CONFIRMED:
                price = market_data["candles"][-1]["close"]
                self._tracking.start(symbol, price)

            # ⏹ final states cleanup
            if next_state in (
                ScenarioState.COMPLETED,
                ScenarioState.CANCELLED,
            ):
                self._tracking.stop(symbol)
                self._zone_manager.clear()
                self._scenario_manager.remove(symbol)
                self._watchlist.remove(symbol)

        scenario.add_event(event)

        if emit_watchlist and event.type in ux_event_types:
            self._watchlist.update(symbol, scenario.state)
            self._watchlist.emit(self._event_bus)

        return state_changed

    def run(self, symbol: str, market_data: dict) -> dict:

        # ===============================
        # 1️⃣ Market context
        # ===============================
        market_context = self._market_context.analyze(
            market_data=market_data,
            event_bus=self._event_bus,
        )

        # ===============================
        # 2️⃣ Scenario
        # ===============================
        scenario = self._scenario_manager.get(symbol)
        if scenario is None:
            scenario = self._scenario_manager.create(
                symbol=symbol,
                direction="LONG",
            )

        # ===============================
        # 3️⃣ Impulse
        # ===============================
        impulse_detector = self._impulse_detectors.get(symbol)
        if impulse_detector is None:
            impulse_detector = ImpulseDetector()
            self._impulse_detectors[symbol] = impulse_detector

        impulse_detector.analyze(
            symbol=symbol,
            market_data=market_data,
            direction=scenario.direction,
            market_context=market_context,
            event_bus=self._event_bus,
        )

        # ===============================
        # 4️⃣ Zones + Reaction
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
        # 5️⃣ Confirmed
        # ===============================
        if scenario.state == ScenarioState.REACTION:
            self._confirmed_detector.analyze(
                symbol=symbol,
                market_data=market_data,
                direction=scenario.direction,
                market_context=market_context,
                event_bus=self._event_bus,
            )

        ux_event_types = {
            EventType.CORRECTION_STARTED,
            EventType.ZONE_REACTED,
            EventType.SCENARIO_CONFIRMED,
            EventType.TRACKING_PROGRESS,
        }

        # ===============================
        # 6️⃣ FSM + Notifications
        # ===============================
        events = self._event_bus.drain()
        state_changed = False

        for index, event in enumerate(events):
            state_changed = (
                self._process_event(
                    event=event,
                    scenario=scenario,
                    market_data=market_data,
                    events=events,
                    event_index=index,
                    symbol=symbol,
                    ux_event_types=ux_event_types,
                    emit_watchlist=True,
                )
                or state_changed
            )

        # ===============================
        # 7️⃣ Watchlist emitted events
        # ===============================
        events = self._event_bus.drain()

        for index, event in enumerate(events):
            state_changed = (
                self._process_event(
                    event=event,
                    scenario=scenario,
                    market_data=market_data,
                    events=events,
                    event_index=index,
                    symbol=symbol,
                    ux_event_types=ux_event_types,
                    emit_watchlist=False,
                )
                or state_changed
            )

        # ===============================
        # 8️⃣ Tracking
        # ===============================
        if scenario.state == ScenarioState.CONFIRMED:
            self._tracking.analyze(
                symbol=symbol,
                market_data=market_data,
                scenario_state=scenario.state,
                direction=scenario.direction,
                event_bus=self._event_bus,
            )

        # ===============================
        # 9️⃣ Tracking events + Watchlist
        # ===============================
        events = self._event_bus.drain()

        for index, event in enumerate(events):
            state_changed = (
                self._process_event(
                    event=event,
                    scenario=scenario,
                    market_data=market_data,
                    events=events,
                    event_index=index,
                    symbol=symbol,
                    ux_event_types=ux_event_types,
                    emit_watchlist=True,
                )
                or state_changed
            )

        events = self._event_bus.drain()

        for index, event in enumerate(events):
            state_changed = (
                self._process_event(
                    event=event,
                    scenario=scenario,
                    market_data=market_data,
                    events=events,
                    event_index=index,
                    symbol=symbol,
                    ux_event_types=ux_event_types,
                    emit_watchlist=False,
                )
                or state_changed
            )

        return {
            "symbol": symbol,
            "state": scenario.state.value,
            "state_changed": state_changed,
            "events": events,
        }
