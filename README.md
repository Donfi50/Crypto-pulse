# Crypto-pulse

Crypto-pulse is an experimental crypto market scanner with **CreateLab**, an AI-assisted video pre-production and game prototyping studio.

## Run CreateLab

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
export OPENAI_API_KEY="your-key-here"  # PowerShell: $env:OPENAI_API_KEY="your-key-here"
streamlit run studio_app.py
```

Optional API configuration: `OPENAI_MODEL` (defaults to `gpt-4o-mini`) and `OPENAI_BASE_URL` (defaults to `https://api.openai.com/v1`).

### Dashboard and project storage

CreateLab now includes a dashboard for browsing and filtering saved projects, downloading plans, and deleting projects. Project metadata and generated text are stored in SQLite at `data/createlab.sqlite3` by default. Set `CREATELAB_DB_PATH` to choose another SQLite file. The database is initialized automatically; local database files are ignored by Git.

This starter has no login or user isolation: anyone using the same deployed app/database can see the same saved projects. Use a private deployment until authentication and per-user access controls are implemented. Streamlit hosting filesystems may be temporary; use a persistent disk or managed database for production deployments.

Video generation currently produces storyboards and prompts, not rendered video files. Game HTML is downloadable but is not executed or previewed by the app. Review generated content and code before using it.

## Deploy on Streamlit Community Cloud

Select this repository, the `main` branch, and `studio_app.py` as the entry point. Add `OPENAI_API_KEY` in app settings under **Secrets**. For reliable long-term project storage, configure a persistent volume/database; the default local SQLite file may not persist across redeploys.

## Crypto scanner

Install dependencies with `pip install -r requirements.txt` and run `python main.py`. Scanner settings are described in `.env.example`. The scanner is experimental and does not provide financial advice.
