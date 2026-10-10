from crypto_pulse.ai_model import build_feature_vector, save_prediction_report, train_dummy_model
from crypto_pulse.config import DEFAULT_SYMBOL
from crypto_pulse.market_data import fetch_historical_klines


def run_ai_signal(symbol: str = DEFAULT_SYMBOL, interval: str = "1h", limit: int = 100):
    candles = fetch_historical_klines(symbol, interval, limit)
    closes = [float(candle["close"]) for candle in candles]

    features = build_feature_vector(closes, window=min(20, len(closes)))
    prediction = train_dummy_model(closes)

    report = {
        "symbol": symbol,
        "interval": interval,
        "last_price": closes[-1],
        "features": features,
        "prediction": prediction,
    }

    saved_path = save_prediction_report(report, filename=f"{symbol.lower()}_prediction.json")
    print(f"AI signal for {symbol}: {prediction['expected_direction']}")
    print(f"Confidence: {prediction['confidence']:.2f}%")
    print(f"Saved prediction report to: {saved_path}")
    return report


if __name__ == "__main__":
    run_ai_signal()
