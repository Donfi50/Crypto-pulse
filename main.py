import argparse
from typing import List

from crypto_pulse.config import DEFAULT_INTERVAL, DEFAULT_LIMIT, DEFAULT_SYMBOL
from crypto_pulse.scanner_report import export_scanner_report
from crypto_pulse.trader import CryptoPulseTrader


def parse_symbols(raw_symbols):
    if raw_symbols is None:
        return [DEFAULT_SYMBOL]
    if isinstance(raw_symbols, str):
        return [symbol.strip() for symbol in raw_symbols.split(",") if symbol.strip()]
    return [str(symbol).strip() for symbol in raw_symbols if str(symbol).strip()]


def scan_symbols(symbols: List[str], interval: str = DEFAULT_INTERVAL, limit: int = DEFAULT_LIMIT):
    """Scan multiple symbols and return ranked signal results."""
    results = []
    for symbol in symbols:
        trader = CryptoPulseTrader(symbol=symbol, interval=interval, limit=limit)
        result = trader.run()
        details = result["signal_details"]

        results.append({
            "symbol": symbol,
            "signal": result["signal"],
            "last_price": result["last_price"],
            "short_sma": details["short_sma"],
            "long_sma": details["long_sma"],
            "ema_fast": details["ema_fast"],
            "ema_slow": details["ema_slow"],
            "rsi": details["rsi"],
            "candles": result["candles"],
        })

    priority = {"BUY": 0, "HOLD": 1, "SELL": 2}
    results.sort(key=lambda item: (priority.get(item["signal"], 99), -abs(item["rsi"] - 50)))
    return results


def print_dashboard(results):
    """Display a compact multi-symbol dashboard in the terminal."""
    print("\nCrypto Pulse Scanner")
    print("=" * 118)
    print(f"{'Symbol':<12} {'Signal':<6} {'Price':>14} {'Short SMA':>12} {'Long SMA':>12} {'RSI':>8}")
    print("-" * 118)

    for row in results:
        print(
            f"{row['symbol']:<12} "
            f"{row['signal']:<6} "
            f"{row['last_price']:>12.2f} "
            f"{row['short_sma']:>12.2f} "
            f"{row['long_sma']:>12.2f} "
            f"{row['rsi']:>7.2f}"
        )

    print("=" * 118)


def scan_cli():
    parser = argparse.ArgumentParser(description="Scan multiple crypto symbols for trade signals.")
    parser.add_argument(
        "--symbols",
        default=DEFAULT_SYMBOL,
        help="Comma-separated symbols, e.g. BTCUSDT,ETHUSDT,SOLUSDT",
    )
    parser.add_argument("--interval", default=DEFAULT_INTERVAL, help="Candle interval, e.g. 1h, 4h")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help="Number of candles per symbol")
    parser.add_argument("--csv-output", default="scanner_report.csv", help="Where to save the scanner CSV report")
    args = parser.parse_args()

    symbols = parse_symbols(args.symbols)
    results = scan_symbols(symbols, interval=args.interval, limit=args.limit)
    print_dashboard(results)

    exported_file = export_scanner_report(results, args.csv_output)
    print(f"\nCSV report saved to: {exported_file}")


if __name__ == "__main__":
    scan_cli()
