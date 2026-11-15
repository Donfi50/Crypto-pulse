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

Optional: set `OPENAI_MODEL` (defaults to `gpt-4o-mini`), `OPENAI_BASE_URL` (defaults to `https://api.openai.com/v1`), or `CREATELAB_DB_PATH` (defaults to `data/createlab.sqlite3`).

## Accounts and project dashboard

CreateLab supports registration, sign-in/sign-out, account details, and password changes after verifying the current password. Passwords are stored as salted PBKDF2-SHA256 hashes, never as plaintext. Each project is associated with its owner; dashboard reads, counts, and deletion are scoped to the signed-in user. SQLite schema updates automatically when the app starts. Older shared projects without a known owner remain unassigned and hidden.

This is an initial account system, not a complete production identity service: email verification, password reset, MFA, and robust cross-device session management are not included. Protect deployments with HTTPS, keep database files private, and use rate limiting and durable database storage before public production use.

## Features and limits

- Generate video storyboards and prompts; actual video rendering is not connected.
- Generate game plans and optionally download HTML; the app never executes generated code.
- Browse, filter, download, and delete your own saved projects.

Run unit tests with:

```bash
python -m unittest discover -s tests
```

## Crypto scanner

Install dependencies with `pip install -r requirements.txt` and run `python main.py`. Scanner settings are described in `.env.example`. The scanner is experimental and does not provide financial advice.
