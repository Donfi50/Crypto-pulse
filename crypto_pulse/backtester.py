from crypto_pulse.strategy import signal_details


def backtest_strategy(candles, initial_balance=1000.0, commission_rate=0.001):
    """Run a simplistic backtest using rolling buy/sell logic."""
    if len(candles) < 30:
        return {
            "final_balance": initial_balance,
            "trades": 0,
            "signal": "HOLD",
            "note": "Not enough candles for a meaningful backtest.",
        }

    balance = float(initial_balance)
    holding_units = 0.0
    entry_price = 0.0
    trade_count = 0

    for index in range(14, len(candles)):
        window = [float(candle["close"]) for candle in candles[:index + 1]]
        current_price = float(candles[index]["close"])
        signal = signal_details(window)["signal"]

        if signal == "BUY" and holding_units == 0:
            holding_units = balance / current_price
            entry_price = current_price
            trade_count += 1

        elif signal == "SELL" and holding_units > 0:
            balance = holding_units * current_price * (1 - commission_rate)
            holding_units = 0.0
            entry_price = 0.0
            trade_count += 1

    if holding_units > 0:
        final_price = float(candles[-1]["close"])
        balance = holding_units * final_price * (1 - commission_rate)

    return {
        "final_balance": balance,
        "trades": trade_count,
        "signal": signal_details([float(candle["close"]) for candle in candles])['signal'],
        "note": "Simple strategy backtest based on SMA/EMA/RSI conditions.",
    }
