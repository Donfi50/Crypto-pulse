import argparse

from crypto_pulse.config import DEFAULT_INTERVAL, DEFAULT_LIMIT, DEFAULT_SYMBOL
from crypto_pulse.exporter import export_candles
from crypto_pulse.scanner import parse_symbols, print_dashboard, scan_symbols
from crypto_pulse.trader import CryptoPulseTrader


def build_parser():
    parser = argparse.ArgumentParser(description="Crypto-pulse trading signal runner")
    parser.add_argument("--symbol", default=DEFAULT_SYMBOL, help="Single symbol, e.g. BTCUSDT")
    parser.add_argument("--symbols", default=None, help="Comma-separated symbols, e.g. BTCUSDT,ETHUSDT,SOLUSDT")
    parser.add_argument("--interval", default=DEFAULT_INTERVAL, help="Candles interval, e.g. 1h or 4h")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help="Number of candles to fetch")
    parser.add_argument("--csv-output", default="market_data.csv", help="Path to export candle data CSV")
    return parser


def main():
    args = build_parser().parse_args()

    if args.symbols:
        symbols = parse_symbols(args.symbols)
        results = scan_symbols(symbols, interval=args.interval, limit=args.limit)
        print_dashboard(results)
        export_candles_for_symbols(results)
        return

    trader = CryptoPulseTrader(symbol=args.symbol, interval=args.interval, limit=args.limit)
    result = trader.run()

    print(f"Symbol: {result['symbol']}")
    print(f"Last price: {result['last_price']:.2f}")
    print(f"Signal: {result['signal']}")
    print(f"Short SMA: {result['signal_details']['short_sma']:.2f}")
    print(f"Long SMA: {result['signal_details']['long_sma']:.2f}")
    print(f"RSI: {result['signal_details']['rsi']:.2f}")
    print(f"Candles analyzed: {result['candles']}")

    csv_path = export_candles(result["candles_data"], args.csv_output)
    print(f"Candles exported to: {csv_path}")


def export_candles_for_symbols(results):
    for row in results:
        symbol = row["symbol"]
        csv_name = f"{symbol.lower()}_{DEFAULT_INTERVAL}.csv"
        export_candles([], csv_name)


if __name__ == "__main__":
    main()
