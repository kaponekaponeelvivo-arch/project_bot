import os
import requests
from dotenv import load_dotenv

from core.scanner_core.events import Event
from core.scanner_core.notifications.formatter import NotificationFormatter


# ⬇️ грузим .env из корня проекта
load_dotenv()


class TelegramNotifier:
    """
    Sends notifications to Telegram Scanner Bot.
    """

    def __init__(self) -> None:
        self._token = os.getenv("SCANNER_BOT_TOKEN")
        self._chat_id = os.getenv("SCANNER_TELEGRAM_CHAT_ID")

        if not self._token:
            raise RuntimeError("SCANNER_BOT_TOKEN not set in .env")

        if not self._chat_id:
            raise RuntimeError("SCANNER_TELEGRAM_CHAT_ID not set in .env")

        self._url = f"https://api.telegram.org/bot{self._token}/sendMessage"

    def handle(self, event: Event) -> None:
        text = NotificationFormatter.format(event)
        if not text:
            return

        payload = {
            "chat_id": self._chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }

        try:
            requests.post(self._url, json=payload, timeout=5)
        except Exception as e:
            print(f"[TELEGRAM NOTIFIER ERROR] {e}")
