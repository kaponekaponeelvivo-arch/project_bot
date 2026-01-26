from typing import Tuple, Optional

from .models import CrossStatus


# =========================
# PAIR EMA (classic cross)
# =========================

def detect_cross(
    ema_fast_prev: float,
    ema_slow_prev: float,
    ema_fast_now: float,
    ema_slow_now: float,
) -> Tuple[bool, str]:
    """
    Detect classic EMA cross.
    Returns (is_cross, direction)
    """
    if ema_fast_prev <= ema_slow_prev and ema_fast_now > ema_slow_now:
        return True, "bullish"

    if ema_fast_prev >= ema_slow_prev and ema_fast_now < ema_slow_now:
        return True, "bearish"

    return False, ""


def classify_status(
    distance_prev: float,
    distance_now: float,
    distance_extreme_threshold: float,
) -> CrossStatus:
    """
    Classify EMA pair state.
    """
    if abs(distance_prev) < 1e-9:
        return CrossStatus.START

    if abs(distance_now) >= distance_extreme_threshold:
        return CrossStatus.EXTREME

    return CrossStatus.STRENGTHEN


# =========================
# EMA CLUSTER 9 / 21 / 50
# =========================

def detect_cluster_direction(
    ema9: float,
    ema21: float,
    ema50: float,
) -> Optional[str]:
    """
    Detect cluster direction.
    """
    if ema9 > ema21 > ema50:
        return "bullish"

    if ema9 < ema21 < ema50:
        return "bearish"

    return None


def classify_cluster_status(
    prev_spread: float,
    now_spread: float,
    extreme_threshold: float,
) -> CrossStatus:
    """
    Classify EMA cluster state.
    """
    if prev_spread <= 1e-9:
        return CrossStatus.START

    if now_spread >= extreme_threshold:
        return CrossStatus.EXTREME

    return CrossStatus.STRENGTHEN
