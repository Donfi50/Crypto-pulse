# CreateLab

CreateLab is a Streamlit app for AI-assisted video pre-production and game concept prototyping.

## Features

- Account registration, sign-in, and sign-out.
- Salted PBKDF2-SHA256 password hashes; plaintext passwords are never saved.
- SQLite-backed user accounts and project records.
- Dashboard browsing, filtering, downloading, and deletion, scoped to the signed-in account.
- Video storyboard and prompt generation; optional downloadable HTML game prototype (not executed by the app).

## Setup

```bash
pip install -r requirements.txt
export OPENAI_API_KEY="your-key-here"
# Optional:
export OPENAI_MODEL="gpt-4o-mini"
export OPENAI_BASE_URL="https://api.openai.com/v1"
export CREATELAB_DB_PATH="data/createlab.sqlite3"
streamlit run studio_app.py
```

On Windows PowerShell, set the API key with `$env:OPENAI_API_KEY="your-key-here"`. Never commit credentials. SQLite is initialized automatically at `data/createlab.sqlite3` unless `CREATELAB_DB_PATH` is set.

Run the test suite with `python -m unittest discover -s tests`.

## Security and deployment limitations

This starter does not include email verification, password reset, MFA, or production-grade login rate limiting. Use HTTPS in deployment and do not expose the database file or backups. For public production, add rate limiting, recovery/verification flows, monitoring, and a managed durable database. SQLite is suitable for a small single-instance deployment, not a horizontally scaled service. Existing projects from the previous shared database are migrated as unowned and are not shown to users.

The app produces video storyboards rather than rendered video. Generated HTML is downloadable only; the app does not execute or preview it.
