from enum import Enum


class ZoneType(Enum):
    """
    Zone classification.

    Order is NOT priority.
    Priority is defined by logic, not enum order.
    """

    STRUCTURE = "structure"
    IMBALANCE = "imbalance"
    RANGE = "range"
    FIBO = "fibo"
