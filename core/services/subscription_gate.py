from datetime import datetime
from core.services.users import UsersService


class SubscriptionGate:
    def __init__(self, users_service: UsersService):
        self.users_service = users_service

    async def has_access(self, telegram_id: int) -> bool:
        user = await self.users_service.get_user(telegram_id)
        if not user or not user.subscription_until:
            return False
        return user.subscription_until > datetime.utcnow()
