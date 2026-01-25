from datetime import datetime
from core.models.user import User
from core.storage.users import UsersStorage


class UsersService:
    def __init__(self, storage: UsersStorage):
        self.storage = storage

    def create_user(self, telegram_id: int, username: str | None) -> User:
        user = User(
            telegram_id=telegram_id,
            username=username,
            created_at=datetime.utcnow(),
            is_active=True,
        )
        self.storage.add(user)
        return user

    def get_all_users(self):
        return self.storage.all()

    def get_user(self, telegram_id: int) -> User | None:
        return self.storage.get(telegram_id)

    def block_user(self, telegram_id: int):
        user = self.get_user(telegram_id)
        if user:
            user.is_active = False

    def unblock_user(self, telegram_id: int):
        user = self.get_user(telegram_id)
        if user:
            user.is_active = True
