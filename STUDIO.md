# CreateLab

CreateLab is a Streamlit app for AI-assisted video pre-production and game concept prototyping.

## Features

- Generate a timed video storyboard or game design and optional HTML prototype.
- Dashboard to browse, filter, open, download, and delete saved projects.
- SQLite persistence for generated project prompts and results.
- Configurable OpenAI-compatible chat-completions endpoint.

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

On Windows PowerShell, set the API key with `$env:OPENAI_API_KEY="your-key-here"`. Never commit credentials.

The SQLite database is automatically initialized at `data/createlab.sqlite3` by default. Set `CREATELAB_DB_PATH` to a different file path if needed. Run database unit tests with `python -m unittest discover -s tests`.

## Important deployment and security notes

There are no user accounts yet, so projects are shared by all visitors using the same database. Do not deploy this publicly with private user content until authentication and authorization are added. SQLite persistence depends on durable storage; hosted ephemeral filesystems can lose database data on restart or redeploy. Configure a persistent disk or managed database for production.

The app creates text plans and prompts; it does not render video files. Generated HTML is offered as a download only and is never executed by the app. Review generated content and code before use.
