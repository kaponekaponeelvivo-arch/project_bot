import os
import io
import requests
import matplotlib.pyplot as plt

from typing import Optional
from dotenv import load_dotenv
from core.scanner_core.events import Event
from core.scanner_core.events.event_types import EventType
from core.scanner_core.notifications.formatter import NotificationFormatter

load_dotenv()


class TelegramNotifier:

    def __init__(self):
        self._token = os.getenv("TELEGRAM_BOT_TOKEN")
        self._chat_id = os.getenv("TELEGRAM_CHAT_ID")

    # ==========================================================
    def handle(self, event: Event) -> None:

        if event.type not in {
            EventType.CORRECTION_STARTED,
            EventType.ZONE_REACTED,
            EventType.SCENARIO_CONFIRMED,
            EventType.SCENARIO_CANCELLED,
            EventType.SCENARIO_COMPLETED,
            EventType.WATCHLIST_UPDATED,
        }:
            return

        message = NotificationFormatter.format(event)

        if not message:
            message = f"{event.type.value} | {event.symbol}"

        image = None

        # 🔥 Строим график для всех фаз сценария
        if event.type in {
            EventType.CORRECTION_STARTED,
            EventType.ZONE_REACTED,
            EventType.SCENARIO_CONFIRMED,
            EventType.SCENARIO_CANCELLED,
            EventType.SCENARIO_COMPLETED,
        }:
            image = self._build_chart(event)

        self._send(message, image)

    # ==========================================================
    def _draw_candles(self, ax, candles):

        for i, c in enumerate(candles):
            color = "green" if c["close"] >= c["open"] else "red"
            ax.plot([i, i], [c["low"], c["high"]], color=color)
            ax.plot([i, i], [c["open"], c["close"]], color=color, linewidth=3)

        ax.grid(True)

    # ==========================================================
    def _build_chart(self, event: Event) -> Optional[bytes]:

        payload = event.payload or {}

        candles_5m = payload.get("candles_5m")
        candles_4h = payload.get("candles_4h")

        if not candles_5m or not candles_4h:
            return None

        direction = payload.get("direction")
        start_index = payload.get("start_index")
        end_index = payload.get("end_index")
        correction_start = payload.get("correction_start_index")
        current_index = payload.get("current_index")
        global_trend = payload.get("global_trend")

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 9))

        # ----- 4H -----
        self._draw_candles(ax1, candles_4h)
        ax1.set_title(f"{event.symbol} | 4H | Global Trend: {global_trend}")

        # ----- 5M -----
        self._draw_candles(ax2, candles_5m)
        ax2.set_title(f"{event.symbol} | 5M")

        # Impulse
        if start_index is not None and end_index is not None:
            color = "green" if direction == "LONG" else "red"
            ax2.axvspan(start_index, end_index, color=color, alpha=0.15)

        # Correction
        if correction_start is not None and current_index is not None:
            color = "yellow" if direction == "LONG" else "blue"
            ax2.axvspan(correction_start, current_index, color=color, alpha=0.25)

        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        plt.close(fig)
        buf.seek(0)

        return buf.read()

    # ==========================================================
    def _send(self, text: str, image: Optional[bytes]) -> None:

        if not self._token or not self._chat_id:
            return

        r = requests.post(
            f"https://api.telegram.org/bot{self._token}/sendMessage",
            data={"chat_id": self._chat_id, "text": text},
        )

        if image:
            requests.post(
                f"https://api.telegram.org/bot{self._token}/sendPhoto",
                files={"photo": image},
                data={"chat_id": self._chat_id},
            )
