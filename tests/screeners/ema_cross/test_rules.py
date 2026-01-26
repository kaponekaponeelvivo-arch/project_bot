import pytest

from core.screeners.ema_cross.rules import detect_cross, classify_status
from core.screeners.ema_cross.models import CrossStatus


def test_detect_bullish_cross():
    is_cross, direction = detect_cross(
        ema_fast_prev=99,
        ema_slow_prev=100,
        ema_fast_now=101,
        ema_slow_now=100,
    )
    assert is_cross is True
    assert direction == "bullish"


def test_detect_bearish_cross():
    is_cross, direction = detect_cross(
        ema_fast_prev=101,
        ema_slow_prev=100,
        ema_fast_now=99,
        ema_slow_now=100,
    )
    assert is_cross is True
    assert direction == "bearish"


def test_no_cross():
    is_cross, direction = detect_cross(
        ema_fast_prev=101,
        ema_slow_prev=100,
        ema_fast_now=102,
        ema_slow_now=100,
    )
    assert is_cross is False
    assert direction == ""


def test_classify_start():
    status = classify_status(
        distance_prev=0.0,
        distance_now=1.0,
        distance_extreme_threshold=10.0,
    )
    assert status == CrossStatus.START


def test_classify_strengthen():
    status = classify_status(
        distance_prev=1.0,
        distance_now=2.0,
        distance_extreme_threshold=10.0,
    )
    assert status == CrossStatus.STRENGTHEN


def test_classify_extreme():
    status = classify_status(
        distance_prev=5.0,
        distance_now=12.0,
        distance_extreme_threshold=10.0,
    )
    assert status == CrossStatus.EXTREME
