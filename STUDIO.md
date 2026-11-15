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
- `main.py` runs the crypto signal scanner
- `crypto_pulse/` contains the market data, strategy, and reporting modules
- `studio_app.py` is an experimental AI studio for video planning and game concept generation

## Run the crypto scanner

1. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the scanner

```bash
python main.py
```

## Run the creative studio

The Streamlit app creates video storyboards and game concept documents from a text prompt. It does not render video files or execute generated game code automatically.

1. Install the requirements above.
2. Set `OPENAI_API_KEY` (or use a Streamlit secret).
3. Optionally set `OPENAI_MODEL` and `OPENAI_BASE_URL`.
4. Launch the app:

```bash
streamlit run studio_app.py
```

The app includes a polished landing page, recent project history, and download tools for Markdown plans and HTML game prototype blocks when provided by the model.

## Environment variables
The crypto scanner can use the `.env` file described in `.env.example`. The creative studio reads API settings from environment variables or Streamlit secrets.

## Notes
The crypto scanner is a starter implementation and does not provide financial advice. The creative studio is a prototype for ideation and concept generation. Any external rendering or deployment should be connected separately.
