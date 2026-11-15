# CreateLab starter

`studio_app.py` adds a small Streamlit creative studio to Crypto-pulse. It uses an OpenAI-compatible chat-completions API for text generation.

## What it can do
- **Video:** produce a timed storyboard, visual direction, and shot-by-shot text-to-video prompts. It does not render a video file; connect a video model/provider for that.
- **Game:** produce a game design brief and self-contained HTML starter code when supported by the model. The site lets you download the HTML file, but does not execute or preview generated code.
- Download each creation plan as Markdown.
- Keep up to ten recent creations in the current Streamlit session, select them from the sidebar, or clear the session history. This is temporary session storage, not a database.

## Configure

```bash
pip install -r requirements.txt
export OPENAI_API_KEY="your-key-here"
# Optional:
export OPENAI_MODEL="gpt-4o-mini"
export OPENAI_BASE_URL="https://api.openai.com/v1"
streamlit run studio_app.py
```

On Windows PowerShell, set the key with `$env:OPENAI_API_KEY="your-key-here"`. For Streamlit Community Cloud, add the key in the app's Secrets settings instead. Never commit a real key.

This is a first web-app scaffold, not a media-rendering pipeline. A next step is to connect a video-generation provider and add persistent project storage.
