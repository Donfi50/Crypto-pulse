# CreateLab

CreateLab is a Streamlit prototype in `studio_app.py` that uses an OpenAI-compatible chat-completions API to produce creative plans.

## Capabilities and limitations

- **Video:** generates storyboards, visual direction, and text-to-video prompts. It does not render video files.
- **Game:** generates game design notes and may include a single fenced HTML prototype block. Users can download that file; the app does not execute or preview generated HTML.
- **History:** stores up to ten creations in Streamlit's active session only. It is not persistent project storage or user account history.
- **Exports:** creation plans download as Markdown; an HTML prototype can be downloaded separately if present.

## Local setup

```bash
pip install -r requirements.txt
export OPENAI_API_KEY="your-key-here"
# Optional settings:
export OPENAI_MODEL="gpt-4o-mini"
export OPENAI_BASE_URL="https://api.openai.com/v1"
streamlit run studio_app.py
```

On Windows PowerShell, set the key with `$env:OPENAI_API_KEY="your-key-here"`. Never commit credentials.

For Streamlit Community Cloud, select `studio_app.py` as the app entry point and add a secret such as:

```toml
OPENAI_API_KEY = "your-key-here"
```

Review generated outputs and code before using them. Connecting a video-generation provider or persistent user/project storage requires additional services and configuration.
