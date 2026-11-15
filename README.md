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
- `studio_app.py` is an experimental web studio for AI-assisted video planning and game prototyping

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

The Streamlit app can create video storyboards and text-to-video prompts, or game design briefs and starter HTML code. It does not render video files, and it does not execute generated game code.

1. Install the requirements above.
2. Set an OpenAI-compatible API key in `OPENAI_API_KEY` (keep it private).
3. Optionally set `OPENAI_MODEL` (defaults to `gpt-4o-mini`) and `OPENAI_BASE_URL` (defaults to `https://api.openai.com/v1`).
4. Start the website locally:

```bash
streamlit run studio_app.py
```

For Streamlit Community Cloud, deploy this repository and add `OPENAI_API_KEY` under **App settings → Secrets**. Never commit API keys to the repository.

The latest results are kept in the current Streamlit session (up to ten). Select a recent creation from the sidebar, download its plan as Markdown, or download a game's fenced HTML block separately. Generated HTML is not executed or previewed by the site. Session history is temporary and is not shared or saved to a database.

## Environment variables
The crypto scanner can use the `.env` file described in `.env.example`. The creative studio reads its API configuration from environment variables or Streamlit secrets.

## Notes
The crypto scanner is a starter implementation and does not provide financial advice. The creative studio is an experimental scaffold; actual video rendering requires connecting a video-generation provider. Review AI-generated content and code before using it.
