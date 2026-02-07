import os
import requests
from dotenv import load_dotenv

from core.scanner_core.events import Event
from core.scanner_core.notifications.formatter import NotificationFormatter


# ⬇️ ВАЖНО: грузим .env
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

        self._api_url = f"https://api.telegram.org/bot{self._token}/sendMessage"

    def handle(self, event: Event) -> None:
        message = NotificationFormatter.format(event)
        if not message:
            return

        payload = {
            "chat_id": self._chat_id,
            "text": message,
            "parse_mode": "HTML",
        }

        try:
            requests.post(self._api_url, json=payload, timeout=5)
        except Exception as e:
            print(f"[TELEGRAM ERROR] {e}")
