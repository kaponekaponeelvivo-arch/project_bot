from typing import Optional

from .models import (
    EmaCrossEvent,
    Timeframe,
    CrossStatus,
    Direction,
)
from .rules import (
    detect_cross,
    classify_status,
    detect_cluster_direction,
    classify_cluster_status,
)


CONTEXT_MAP = {
    Timeframe.M15: {
        CrossStatus.START: "Признаки возможного локального слома текущего движения",
        CrossStatus.STRENGTHEN: "Признаки локального изменения структуры усиливаются",
        CrossStatus.EXTREME: "Рынок может находиться в состоянии локального перегрева",
    },
    Timeframe.H1: {
        CrossStatus.START: "Начинается формирование нового среднесрочного импульса",
        CrossStatus.STRENGTHEN: "Среднесрочное движение усиливается",
        CrossStatus.EXTREME: "Текущее движение достигло экстремальной стадии",
    },
    Timeframe.H4: {
        CrossStatus.START: "Начинается формирование нового среднесрочного импульса",
        CrossStatus.STRENGTHEN: "Среднесрочное движение усиливается",
        CrossStatus.EXTREME: "Текущее движение достигло экстремальной стадии",
    },
    Timeframe.D1: {
        CrossStatus.START: "Фиксируется смена глобального тренда",
        CrossStatus.STRENGTHEN: "Глобальный тренд подтверждается",
        CrossStatus.EXTREME: "Глобальное движение выглядит перегретым",
    },
}


class EmaCrossDetector:
    def __init__(
        self,
        symbol: str,
        timeframe: Timeframe,
        mode: str,
        distance_extreme_threshold: float,
    ):
        self.symbol = symbol
        self.timeframe = timeframe
        self.mode = mode
        self.distance_extreme_threshold = distance_extreme_threshold

    # =========================
    # CLASSIC EMA CROSS
    # =========================

    def detect(
        self,
        ema_fast_prev: float,
        ema_slow_prev: float,
        ema_fast_now: float,
        ema_slow_now: float,
    ) -> Optional[EmaCrossEvent]:

        is_cross, direction_raw = detect_cross(
            ema_fast_prev,
            ema_slow_prev,
            ema_fast_now,
            ema_slow_now,
        )

        if not is_cross:
            return None

        distance_prev = ema_fast_prev - ema_slow_prev
        distance_now = ema_fast_now - ema_slow_now

        status = classify_status(
            distance_prev=distance_prev,
            distance_now=distance_now,
            distance_extreme_threshold=self.distance_extreme_threshold,
        )

        direction = (
            Direction.BULLISH
            if direction_raw == "bullish"
            else Direction.BEARISH
        )

        context = CONTEXT_MAP[self.timeframe][status]

        return EmaCrossEvent(
            symbol=self.symbol,
            timeframe=self.timeframe,
            mode=self.mode,
            status=status,
            direction=direction,
            context=context,
        )

    # =========================
    # EMA CLUSTER 9 / 21 / 50
    # =========================

    def detect_cluster(
        self,
        ema9_prev: float,
        ema21_prev: float,
        ema50_prev: float,
        ema9_now: float,
        ema21_now: float,
        ema50_now: float,
    ) -> Optional[EmaCrossEvent]:

        prev_direction = detect_cluster_direction(
            ema9_prev, ema21_prev, ema50_prev
        )
        now_direction = detect_cluster_direction(
            ema9_now, ema21_now, ema50_now
        )

        if now_direction is None:
            return None

        prev_spread = abs(ema9_prev - ema50_prev)
        now_spread = abs(ema9_now - ema50_now)

        status = classify_cluster_status(
            prev_spread=prev_spread,
            now_spread=now_spread,
            extreme_threshold=self.distance_extreme_threshold,
        )

        direction = (
            Direction.BULLISH
            if now_direction == "bullish"
            else Direction.BEARISH
        )

        context = CONTEXT_MAP[self.timeframe][status]

        return EmaCrossEvent(
            symbol=self.symbol,
            timeframe=self.timeframe,
            mode=self.mode,  # "ema_cluster_9_21_50"
            status=status,
            direction=direction,
            context=context,
        )
