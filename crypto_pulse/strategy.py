from statistics import mean


def generate_signal(prices):
    """Generate a simple trade signal using moving-average momentum."""
    if len(prices) < 5:
        return "HOLD"

    short_window = mean(prices[-5:])
    long_window = mean(prices[-20:]) if len(prices) >= 20 else mean(prices)

    if short_window > long_window:
        return "BUY"
    if short_window < long_window:
        return "SELL"
    return "HOLD"
