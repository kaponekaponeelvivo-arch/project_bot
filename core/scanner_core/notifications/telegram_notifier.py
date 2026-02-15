import os
import tempfile
import requests
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from dotenv import load_dotenv

from core.scanner_core.events import Event
from core.scanner_core.events.event_types import EventType
from core.scanner_core.notifications.formatter import NotificationFormatter
from core.scanner_core.live.bybit_client import BybitClient


load_dotenv()


class TelegramNotifier:

    def __init__(self) -> None:
        self._token = os.getenv("SCANNER_BOT_TOKEN")
        self._chat_id = os.getenv("SCANNER_TELEGRAM_CHAT_ID")

        if not self._token:
            raise RuntimeError("SCANNER_BOT_TOKEN not set")

        if not self._chat_id:
            raise RuntimeError("SCANNER_TELEGRAM_CHAT_ID not set")

        self._url = f"https://api.telegram.org/bot{self._token}/sendMessage"
        self._client = BybitClient()

    # =========================
    # Candle drawing
    # =========================
    def _draw_candles(self, ax, candles):
        for i, c in enumerate(candles):
            open_ = c["open"]
            close = c["close"]
            high = c["high"]
            low = c["low"]

            bullish = "#26a69a"
            bearish = "#ef5350"
            color = bullish if close >= open_ else bearish

            ax.plot([i, i], [low, high], color=color, linewidth=1)

            lower = min(open_, close)
            height = abs(close - open_)
            rect = Rectangle(
                (i - 0.35, lower),
                0.7,
                height if height > 0 else 0.000001,
                facecolor=color,
                edgecolor=color,
            )
            ax.add_patch(rect)

        ax.set_xlim(-1, len(candles))
        ax.grid(True, linestyle="--", alpha=0.2)

    # =========================
    # Trend detection (4H)
    # =========================
    def _detect_trend(self, candles):
        if len(candles) < 30:
            return "UNKNOWN"

        closes = [c["close"] for c in candles[-30:]]
        first = closes[0]
        last = closes[-1]

        change = (last - first) / first

        if change > 0.02:
            return "TREND UP"
        elif change < -0.02:
            return "TREND DOWN"
        else:
            return "RANGE"

    # =========================
    # MAIN
    # =========================
    def handle(self, event: Event) -> None:

        if event.type not in {
            EventType.CORRECTION_STARTED,
            EventType.WATCHLIST_UPDATED,
        }:
            return

        text = NotificationFormatter.format(event)
        if not text:
            return

        if event.type == EventType.CORRECTION_STARTED:

            symbol = event.symbol
            payload = event.payload or {}
            duration = payload.get("duration_candles", 6)

            try:
                data_4h = self._client.get_candles(
                    symbol=symbol,
                    interval="240",
                    limit=120,
                )
                candles_4h = data_4h.get("candles", [])

                data_5m = self._client.get_candles(
                    symbol=symbol,
                    interval="5",
                    limit=120,
                )
                candles_5m = data_5m.get("candles", [])

            except Exception as e:
                print(f"[TELEGRAM ERROR] Failed to fetch candles: {e}")
                self._send_message(text)
                return

            if not candles_4h:
                self._send_message(text)
                return

            # 🔥 Detect trend
            trend = self._detect_trend(candles_4h)

            # add trend to caption
            text = f"{text}\n\n<b>Глобальный тренд:</b> {trend}"

            tmp_path = None

            try:
                fig, axes = plt.subplots(2, 1, figsize=(12, 8))

                ax1 = axes[0]
                ax1.set_title(f"{symbol} • 4H")
                self._draw_candles(ax1, candles_4h)

                start_index = max(len(candles_4h) - duration - 1, 0)
                end_index = len(candles_4h) - 1

                ax1.axvspan(
                    start_index,
                    end_index,
                    color="#2196f3",
                    alpha=0.15,
                )

                ax2 = axes[1]
                ax2.set_title(f"{symbol} • 5M")
                self._draw_candles(ax2, candles_5m)

                plt.tight_layout()

                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                    tmp_path = tmp.name

                plt.savefig(tmp_path, dpi=150)
                plt.close()

                photo_url = f"https://api.telegram.org/bot{self._token}/sendPhoto"

                with open(tmp_path, "rb") as photo:
                    response = requests.post(
                        photo_url,
                        data={
                            "chat_id": self._chat_id,
                            "caption": text,
                            "parse_mode": "HTML",
                        },
                        files={"photo": photo},
                        timeout=10,
                    )

                print(f"[TELEGRAM PHOTO] status_code={response.status_code}")

            except Exception as e:
                print(f"[TELEGRAM ERROR] {e}")
                self._send_message(text)

            finally:
                if tmp_path and os.path.exists(tmp_path):
                    os.remove(tmp_path)

            return

        self._send_message(text)

    # =========================
    def _send_message(self, text: str):
        payload = {
            "chat_id": self._chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }

        response = requests.post(self._url, json=payload, timeout=5)
        print(f"[TELEGRAM MESSAGE] status_code={response.status_code}")
