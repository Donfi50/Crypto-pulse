import csv
import json
from pathlib import Path
from typing import List

from crypto_pulse.config import DEFAULT_INTERVAL, DEFAULT_LIMIT, DEFAULT_SYMBOL
from crypto_pulse.market_data import fetch_historical_klines
from crypto_pulse.unified_scorer import combine_signals


def scan_with_unified_scoring(symbols: List[str], interval: str = DEFAULT_INTERVAL, limit: int = DEFAULT_LIMIT):
    """Scan multiple symbols and rank by combined technical + AI score."""
    results = []

    for symbol in symbols:
        try:
            candles = fetch_historical_klines(symbol, interval, limit)
            closes = [float(candle["close"]) for candle in candles]
            last_price = closes[-1]

            combined = combine_signals(closes)

            results.append({
                "symbol": symbol,
                "last_price": last_price,
                "recommendation": combined["recommendation"],
                "confidence": combined["confidence"],
                "technical_signal": combined["technical_signal"],
                "ai_signal": combined["ai_signal"],
                "rsi": combined["rsi"],
                "reasoning": combined["reasoning"],
            })
        except Exception as e:
            print(f"Error scanning {symbol}: {e}")
            continue

    priority = {"BUY": 0, "HOLD": 1, "SELL": 2}
    results.sort(key=lambda x: (priority.get(x["recommendation"], 99), -x["confidence"]))
    return results


def export_unified_report(results, csv_file="unified_report.csv", json_file="unified_report.json"):
    """Export combined scoring results to CSV and JSON."""
    with open(csv_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=[
                "symbol",
                "recommendation",
                "confidence",
                "last_price",
                "technical_signal",
                "ai_signal",
                "rsi",
            ],
        )
        writer.writeheader()
        for row in results:
            writer.writerow({
                "symbol": row["symbol"],
                "recommendation": row["recommendation"],
                "confidence": row["confidence"],
                "last_price": row["last_price"],
                "technical_signal": row["technical_signal"],
                "ai_signal": row["ai_signal"],
                "rsi": row["rsi"],
            })

    json_path = Path(json_file)
    json_path.write_text(json.dumps(results, indent=2), encoding="utf-8")

    return csv_file, json_file


def print_unified_dashboard(results):
    """Display unified scoring results in a clean terminal table."""
    print("\n" + "=" * 140)
    print(f"{'Symbol':<12} {'Recommendation':<15} {'Confidence':<12} {'Price':>14} {'Technical':<12} {'AI':<12} {'RSI':>8}")
    print("-" * 140)

    for row in results:
        print(
            f"{row['symbol']:<12} "
            f"{row['recommendation']:<15} "
            f"{row['confidence']:>10.2f}% "
            f"{row['last_price']:>12.2f} "
            f"{row['technical_signal']:<12} "
            f"{row['ai_signal']:<12} "
            f"{row['rsi']:>7.2f}"
        )

    print("=" * 140 + "\n")
