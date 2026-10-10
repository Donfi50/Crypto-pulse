from crypto_pulse.market_data import fetch_historical_klines
from crypto_pulse.strategy import signal_details


class CryptoPulseTrader:
    def __init__(self, symbol: str, interval: str = "1h", limit: int = 100):
        self.symbol = symbol
        self.interval = interval
        self.limit = limit

    def run(self):
        candles = fetch_historical_klines(self.symbol, self.interval, self.limit)

        if not candles:
            raise ValueError(f"No market data returned for {self.symbol}.")

        closes = [float(candle["close"]) for candle in candles]
        details = signal_details(closes)
        last_price = closes[-1]

        return {
            "symbol": self.symbol,
            "interval": self.interval,
            "last_price": last_price,
            "signal": details["signal"],
            "signal_details": details,
            "candles": len(candles),
            "candles_data": candles,
        }
