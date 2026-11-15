# Crypto-pulse

Crypto-pulse is a starter project for experimenting with crypto market signals and paper trading. It also includes **CreateLab**, an experimental AI-assisted studio for video pre-production and game prototyping.

## CreateLab: AI video and game studio

CreateLab turns a text prompt into a video storyboard or a game concept. Game outputs may include a downloadable HTML prototype. It does not render video files or execute generated game code. Up to ten creations are kept in the active Streamlit session; they are not stored in a database.

### Run locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
export OPENAI_API_KEY="your-key-here"  # PowerShell: $env:OPENAI_API_KEY="your-key-here"
streamlit run studio_app.py
```

Optional configuration:

```bash
export OPENAI_MODEL="gpt-4o-mini"
export OPENAI_BASE_URL="https://api.openai.com/v1"
```

Keep API keys secret. Do not commit them to the repository.

### Deploy on Streamlit Community Cloud

1. Create a new app and select this repository, its `main` branch, and `studio_app.py` as the entry point.
2. In the deployed app's settings, add `OPENAI_API_KEY` under **Secrets** using TOML syntax:

   ```toml
   OPENAI_API_KEY = "your-key-here"
   ```

3. Redeploy. The app installs dependencies from `requirements.txt`.

### Features

- Video storyboard, visual direction, and shot-by-shot text-to-video prompts.
- Game design brief and optional HTML prototype download.
- Up to ten recent session creations with Markdown plan downloads.
- OpenAI-compatible chat-completions endpoint configuration.

## Crypto scanner

Install dependencies with `pip install -r requirements.txt`, then run `python main.py`. See `.env.example` for market scanner configuration. The scanner is experimental and does not provide financial advice.
