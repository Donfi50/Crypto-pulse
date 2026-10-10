import requests

from crypto_pulse.config import API_BASE_URL, DEFAULT_INTERVAL, DEFAULT_LIMIT


def fetch_historical_klines(symbol: str, interval: str = DEFAULT_INTERVAL, limit: int = DEFAULT_LIMIT):
    """Fetch OHLCV candlestick data from Binance."""
    url = f"{API_BASE_URL}/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit,
    }

    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()

    raw_data = response.json()
    candles = []

    for item in raw_data:
        candles.append({
            "open_time": item[0],
            "open": float(item[1]),
            "high": float(item[2]),
            "low": float(item[3]),
            "close": float(item[4]),
            "volume": float(item[5]),
            "close_time": item[6],
        })

    return candles
