import argparse

from crypto_pulse.config import DEFAULT_INTERVAL, DEFAULT_LIMIT, DEFAULT_SYMBOL
from crypto_pulse.unified_scanner import export_unified_report, print_unified_dashboard, scan_with_unified_scoring


def parse_symbols(raw_input):
    """Parse comma-separated or space-separated symbol list."""
    if raw_input is None:
        return [DEFAULT_SYMBOL]
    if isinstance(raw_input, str):
        return [s.strip().upper() for s in raw_input.replace(",", " ").split() if s.strip()]
    return [str(s).strip().upper() for s in raw_input if str(s).strip()]


def main():
    parser = argparse.ArgumentParser(
        description="Crypto-pulse unified scanner: Technical + AI signals with confidence scoring."
    )
    parser.add_argument(
        "--symbols",
        default=DEFAULT_SYMBOL,
        help="Symbols to scan (comma or space separated). Default: BTCUSDT",
    )
    parser.add_argument("--interval", default=DEFAULT_INTERVAL, help="Candle interval (1m, 5m, 1h, 4h, 1d)")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help="Number of candles per symbol")
    parser.add_argument("--csv-output", default="unified_report.csv", help="CSV export path")
    parser.add_argument("--json-output", default="unified_report.json", help="JSON export path")
    args = parser.parse_args()

    symbols = parse_symbols(args.symbols)
    print(f"\nScanning {len(symbols)} symbols: {', '.join(symbols)}")
    print(f"Interval: {args.interval}, Limit: {args.limit}")

    results = scan_with_unified_scoring(symbols, interval=args.interval, limit=args.limit)
    print_unified_dashboard(results)

    csv_file, json_file = export_unified_report(results, args.csv_output, args.json_output)
    print(f"CSV report saved to: {csv_file}")
    print(f"JSON report saved to: {json_file}")


if __name__ == "__main__":
    main()
