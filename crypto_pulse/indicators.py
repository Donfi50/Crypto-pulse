def sma(values, window):
    """Simple moving average."""
    if not values:
        return 0.0
    if len(values) < window:
        window = len(values)
    return sum(values[-window:]) / window


def ema(values, span):
    """Exponential moving average."""
    if not values:
        return 0.0
    if len(values) == 1:
        return float(values[0])

    alpha = 2 / (span + 1)
    result = float(values[0])
    for value in values[1:]:
        result = (alpha * float(value)) + ((1 - alpha) * result)
    return result


def rsi(values, periods=14):
    """Relative strength index, scaled from 0 to 100."""
    if len(values) < periods + 1:
        return 50.0

    changes = [float(values[i]) - float(values[i - 1]) for i in range(1, len(values))]
    gains = [max(change, 0) for change in changes[-periods:]]
    losses = [abs(min(change, 0)) for change in changes[-periods:]]

    avg_gain = sum(gains) / len(gains)
    avg_loss = sum(losses) / len(losses)

    if avg_loss == 0:
        return 100.0 if avg_gain >= 0 else 50.0

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))
