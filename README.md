# Crypto-pulse

Crypto-pulse is a starter project for building a crypto trading strategy with AI-inspired signal generation.

The project is intentionally simple and modular so you can extend it with:
- real market data collection
- technical indicators
- ML-based prediction models
- backtesting
- bot execution logic
- paper trading or live trading integration

## Project goals
- Collect cryptocurrency price data
- Generate trade signals based on price momentum
- Provide a clean starting point for experiments
- Keep the project easy to run and extend

## Current structure
- `main.py` runs a basic signal check
- `crypto_pulse/market_data.py` fetches market candles from Binance
- `crypto_pulse/strategy.py` generates simple buy/sell/hold signals
- `crypto_pulse/trader.py` combines the pipeline into one workflow

## Setup

1. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the project

```bash
python main.py
```

## Environment variables
Copy the example file and adjust the values if needed:

```bash
cp .env.example .env
```

## Example output

```text
Symbol: BTCUSDT
Last price: 64123.45
Signal: BUY
```

## Notes
This is a starter implementation. It does not provide live trading or financial advice. It is intended to be a foundation for experimentation and learning.
