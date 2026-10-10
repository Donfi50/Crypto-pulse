import csv
import json
from pathlib import Path


class Dashboard:
    """Simple terminal dashboard for signal output."""

    def __init__(self, results):
        self.results = results

    def render(self):
        print("\nCrypto Pulse Dashboard")
        print("=" * 140)
        print(f"{'Symbol':<12} {'Recommendation':<15} {'Confidence':<12} {'Price':>14} {'Technical':<12} {'AI':<12} {'RSI':>8}")
        print("-" * 140)

        for row in self.results:
            print(
                f"{row['symbol']:<12} "
                f"{row['recommendation']:<15} "
                f"{row['confidence']:>10.2f}% "
                f"{row['last_price']:>12.2f} "
                f"{row['technical_signal']:<12} "
                f"{row['ai_signal']:<12} "
                f"{row['rsi']:>7.2f}"
            )

        print("=" * 140)


def export_dashboard_json(results, filename="dashboard_report.json"):
    """Save dashboard report to JSON."""
    path = Path(filename)
    path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    return str(path)


def export_dashboard_csv(results, filename="dashboard_report.csv"):
    """Save dashboard report to CSV."""
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
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
    return filename
