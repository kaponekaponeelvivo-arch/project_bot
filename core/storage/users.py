from typing import Dict, List
from core.models.user import User


class UsersStorage:
    def __init__(self):
        self._users: Dict[int, User] = {}

    def add(self, user: User):
        self._users[user.telegram_id] = user

    def get(self, telegram_id: int) -> User | None:
        return self._users.get(telegram_id)

    def all(self) -> List[User]:
        return list(self._users.values())
