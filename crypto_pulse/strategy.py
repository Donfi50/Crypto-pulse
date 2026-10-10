from crypto_pulse.indicators import ema, rsi, sma


def signal_details(prices):
    """Return a structured signal and associated indicators."""
    if not prices:
        return {
            "signal": "HOLD",
            "short_sma": 0.0,
            "long_sma": 0.0,
            "ema_fast": 0.0,
            "ema_slow": 0.0,
            "rsi": 50.0,
        }

    short_sma = sma(prices, 5)
    long_sma = sma(prices, 20)
    ema_fast = ema(prices, 9)
    ema_slow = ema(prices, 21)
    rsi_value = rsi(prices, 14)

    if short_sma > long_sma and rsi_value > 55 and ema_fast > ema_slow:
        signal = "BUY"
    elif short_sma < long_sma and rsi_value < 45 and ema_fast < ema_slow:
        signal = "SELL"
    else:
        signal = "HOLD"

    return {
        "signal": signal,
        "short_sma": short_sma,
        "long_sma": long_sma,
        "ema_fast": ema_fast,
        "ema_slow": ema_slow,
        "rsi": rsi_value,
    }


def generate_signal(prices):
    """Backward-compatible string signal generator."""
    return signal_details(prices)["signal"]
