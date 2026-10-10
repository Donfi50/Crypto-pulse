import csv


def export_scanner_report(rows, filename="scanner_report.csv"):
    """Export a multi-symbol signal scan to CSV."""
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=[
                "symbol",
                "signal",
                "last_price",
                "short_sma",
                "long_sma",
                "ema_fast",
                "ema_slow",
                "rsi",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({
                "symbol": row["symbol"],
                "signal": row["signal"],
                "last_price": row["last_price"],
                "short_sma": row["short_sma"],
                "long_sma": row["long_sma"],
                "ema_fast": row["ema_fast"],
                "ema_slow": row["ema_slow"],
                "rsi": row["rsi"],
            })
    return filename
