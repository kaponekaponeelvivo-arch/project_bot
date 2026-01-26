from datetime import datetime, timezone

from core.services.subscriptions import SubscriptionsService
from core.storage.postgres_notification_limits import (
    PostgresNotificationLimitsStorage,
)

FREE_DAILY_LIMIT = 5


class NotificationGate:
    def __init__(
        self,
        limits_storage: PostgresNotificationLimitsStorage,
        subscriptions_service: SubscriptionsService,
    ):
        self.limits_storage = limits_storage
        self.subscriptions_service = subscriptions_service

    @staticmethod
    def _today_utc():
        return datetime.now(timezone.utc).date()

    async def can_send(self, telegram_id: int) -> bool:
        if await self.subscriptions_service.has_active_subscription(
            telegram_id
        ):
            return True

        today = self._today_utc()
        sent = await self.limits_storage.get_count(telegram_id, today)
        return sent < FREE_DAILY_LIMIT

    async def register_send(self, telegram_id: int) -> None:
        today = self._today_utc()
        await self.limits_storage.increment(telegram_id, today)
