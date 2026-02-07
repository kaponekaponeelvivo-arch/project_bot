from core.scanner_core.watchlist import Watchlist


def main():
    print("=== WATCHLIST MANUAL TEST ===")

    watchlist = Watchlist()

    # ⚠️ Упрощённые фейковые свечи
    market_data = {
        "candles": [
            {
                "open": 100,
                "high": 110,
                "low": 99,
                "close": 108,
                "volume": 2000,
            },
            {
                "open": 108,
                "high": 115,
                "low": 107,
                "close": 114,
                "volume": 2200,
            },
        ]
    }

    # прогоняем один символ
    watchlist.process("SOLUSDT", market_data)

    print("\n--- SUMMARY ---")
    print(watchlist.summary())


if __name__ == "__main__":
    main()
