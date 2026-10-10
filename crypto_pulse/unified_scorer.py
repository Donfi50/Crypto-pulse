from crypto_pulse.ai_model import train_dummy_model
from crypto_pulse.strategy import signal_details


def combine_signals(prices):
    """Merge technical signal with AI prediction for a unified recommendation."""
    if not prices or len(prices) < 5:
        return {
            "recommendation": "HOLD",
            "confidence": 0.0,
            "reasoning": "Insufficient data",
        }

    technical = signal_details(prices)
    ai_prediction = train_dummy_model(prices)

    tech_signal = technical["signal"]
    rsi = technical["rsi"]
    ai_direction = ai_prediction.get("expected_direction", "HOLD")
    ai_confidence = ai_prediction.get("confidence", 0.0)

    vote_buy = 0
    vote_sell = 0
    vote_hold = 0

    if tech_signal == "BUY":
        vote_buy += 1
    elif tech_signal == "SELL":
        vote_sell += 1
    else:
        vote_hold += 1

    if ai_direction == "BUY":
        vote_buy += 1
    elif ai_direction == "SELL":
        vote_sell += 1
    else:
        vote_hold += 1

    if rsi > 60:
        vote_buy += 0.5
    elif rsi < 40:
        vote_sell += 0.5
    else:
        vote_hold += 0.5

    if vote_buy > vote_sell and vote_buy > vote_hold:
        recommendation = "BUY"
    elif vote_sell > vote_buy and vote_sell > vote_hold:
        recommendation = "SELL"
    else:
        recommendation = "HOLD"

    confidence = max(vote_buy, vote_sell, vote_hold) / 3.0 * 100

    reasoning = f"Technical: {tech_signal}, AI: {ai_direction}, RSI: {rsi:.2f}"

    return {
        "recommendation": recommendation,
        "confidence": confidence,
        "reasoning": reasoning,
        "technical_signal": tech_signal,
        "ai_signal": ai_direction,
        "rsi": rsi,
    }
