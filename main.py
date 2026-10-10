from crypto_pulse.config import DEFAULT_SYMBOL
from crypto_pulse.trader import CryptoPulseTrader


def main():
    trader = CryptoPulseTrader(symbol=DEFAULT_SYMBOL, interval="1h", limit=100)
    result = trader.run()

    print(f"Symbol: {result['symbol']}")
    print(f"Last price: {result['last_price']:.2f}")
    print(f"Signal: {result['signal']}")
    print(f"Candles analyzed: {result['candles']}")


if __name__ == "__main__":
    main()
