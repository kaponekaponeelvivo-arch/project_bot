class TradingConfig:

    # ===============================
    # TIMEFRAMES
    # ===============================
    TREND_TF = "4H"
    IMPULSE_TF = "1H"
    REACTION_TF = "15M"
    ENTRY_TF = "5M"

    # ===============================
    # IMPULSE
    # ===============================
    LOOKBACK_CANDLES = 300
    MIN_IMPULSE_PERCENT = 25.0
    MIN_IMPULSE_CANDLES = 15

    # ===============================
    # CORRECTION
    # ===============================
    MIN_CORRECTION_PERCENT = 30.0
    MAX_CORRECTION_PERCENT = 80.0

    # ===============================
    # FIB LEVELS
    # ===============================
    FIB_LEVELS = [0.5, 0.618, 0.782]

    # ===============================
    # STOP BUFFER
    # ===============================
    STOP_BUFFER_PERCENT = 1.0

    # ===============================
    # TP
    # ===============================
    RR_TP1 = 1.0
    RR_TP2 = 2.0
