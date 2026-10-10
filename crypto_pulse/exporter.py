import csv
from pathlib import Path


def export_candles(candles, filename="market_data.csv"):
    """Export OHLCV data to CSV for analysis and backtesting."""
    output_path = Path(filename)

    with output_path.open("w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["open_time", "open", "high", "low", "close", "volume", "close_time"])
        for candle in candles:
            writer.writerow([
                candle.get("open_time", ""),
                candle.get("open", ""),
                candle.get("high", ""),
                candle.get("low", ""),
                candle.get("close", ""),
                candle.get("volume", ""),
                candle.get("close_time", ""),
            ])

    return str(output_path)
