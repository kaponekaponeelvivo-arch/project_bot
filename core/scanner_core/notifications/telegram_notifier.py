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
        }:
            return

        message = NotificationFormatter.format(event)
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
        candles_1h = payload.get("candles_1h")
        candles_4h = payload.get("candles_4h")

        if not candles_5m or not candles_1h or not candles_4h:
            return None

        direction = payload.get("direction")
        global_trend = payload.get("global_trend")

        entry = payload.get("entry_price")
        stop = payload.get("stop_price")
        tp1 = payload.get("tp1_price")
        tp2 = payload.get("tp2_price")
        tp3 = payload.get("tp3_price")

        zone_from = payload.get("zone_from")
        zone_to = payload.get("zone_to")
        zone_type = payload.get("zone_type")

        fig, (ax4h, ax1h, ax5m) = plt.subplots(3, 1, figsize=(12, 14))

        # ======================================================
        # 4H – GLOBAL
        # ======================================================
        self._draw_candles(ax4h, candles_4h)
        ax4h.set_title(f"{event.symbol} | 4H | Trend: {global_trend}")

        # ======================================================
        # 1H – IMPULSE / ZONE
        # ======================================================
        self._draw_candles(ax1h, candles_1h)
        ax1h.set_title(f"{event.symbol} | 1H")

        if zone_from and zone_to:
            color = "blue"
            ax1h.axhspan(zone_from, zone_to, color=color, alpha=0.2)
            ax1h.text(
                0,
                zone_to,
                zone_type,
                color="blue",
                fontsize=9,
            )

        # ======================================================
        # 5M – ENTRY / TP / SL
        # ======================================================
        self._draw_candles(ax5m, candles_5m)
        ax5m.set_title(f"{event.symbol} | 5M")

        if entry:
            ax5m.axhline(entry, color="green", linestyle="--")

        if stop:
            ax5m.axhline(stop, color="red", linestyle="--")

        if tp1:
            ax5m.axhline(tp1, color="green", alpha=0.6)

        if tp2:
            ax5m.axhline(tp2, color="green", alpha=0.9)

        if tp3:
            ax5m.axhline(tp3, color="green", linestyle=":")

        if event.type == EventType.SCENARIO_COMPLETED:
            ax5m.set_title(f"{event.symbol} | COMPLETED")

        if event.type == EventType.SCENARIO_CANCELLED:
            ax5m.set_title(f"{event.symbol} | CANCELLED")

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

        requests.post(
            f"https://api.telegram.org/bot{self._token}/sendMessage",
            data={"chat_id": self._chat_id, "text": text},
        )

        if image:
            requests.post(
                f"https://api.telegram.org/bot{self._token}/sendPhoto",
                files={"photo": image},
                data={"chat_id": self._chat_id},
            )
