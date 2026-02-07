from enum import Enum


class NotifyTarget(Enum):
    ADMIN = "admin"
    SCANNER = "scanner"
    USER = "user"
