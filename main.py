from crypto_pulse.backtester import backtest_strategy
from crypto_pulse.config import DEFAULT_SYMBOL
from crypto_pulse.trader import CryptoPulseTrader


def main():
    trader = CryptoPulseTrader(symbol=DEFAULT_SYMBOL, interval="1h", limit=100)
    result = trader.run()

    print(f"Symbol: {result['symbol']}")
    print(f"Last price: {result['last_price']:.2f}")
    print(f"Signal: {result['signal']}")
    print(f"Short SMA: {result['signal_details']['short_sma']:.2f}")
    print(f"Long SMA: {result['signal_details']['long_sma']:.2f}")
    print(f"RSI: {result['signal_details']['rsi']:.2f}")
    print(f"Candles analyzed: {result['candles']}")

    backtest = backtest_strategy(result["candles_data"])
    print(f"Backtest final balance: ${backtest['final_balance']:.2f}")
    print(f"Trades executed: {backtest['trades']}")


if __name__ == "__main__":
    main()
