import os
import re
from datetime import datetime, timezone

import requests
import streamlit as st


API_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


st.set_page_config(
    page_title="CreateLab — AI Video & Game Studio",
    page_icon="🎬",
    layout="wide",
)

st.markdown(
    """
    <style>
      .stApp { background: #0b0d13; color: #eef0f6; }
      [data-testid="stSidebar"] { background: #11141d; }
      .hero { padding: 2rem 0 1rem; }
      .hero h1 { font-size: clamp(2.4rem, 5vw, 4rem); letter-spacing: -0.06em; margin: 0; }
      .hero p { color: #a4a9b8; font-size: 1.1rem; max-width: 700px; }
      .eyebrow { color: #a78bfa; text-transform: uppercase; letter-spacing: .16em; font-size: .75rem; font-weight: 700; }
      div[data-testid="stForm"] { border: 1px solid #252938; border-radius: 18px; padding: 1.25rem; background: #11141d; }
      .note { color: #a4a9b8; font-size: .9rem; }
    </style>
    <div class="hero">
      <div class="eyebrow">Your creative co-pilot</div>
      <h1>Make something <span style="color:#a78bfa">unreal.</span></h1>
      <p>Turn an idea into a video production plan or a game concept and starter code. One prompt is all you need to begin.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("## CreateLab")
    creation_type = st.radio("What are you making?", ["Video", "Game"], horizontal=True)
    st.divider()
    st.caption("AI settings")
    st.caption(f"Model: `{MODEL}`")
    st.caption("Your API key stays on the server and is never shown in the page.")
    st.divider()
    st.caption("Video rendering is not connected yet. This starter creates a production-ready storyboard and prompts; connect a video provider to render clips.")

with st.form("creation_form"):
    prompt = st.text_area(
        "Describe your idea",
        placeholder=(
            "A cozy sci-fi short about a tiny robot discovering a garden on Mars..."
            if creation_type == "Video"
            else "A cheerful platform game where a fox collects stars in a forest..."
        ),
        max_chars=2000,
        height=135,
    )
    left, right = st.columns(2)
    with left:
        style = st.selectbox(
            "Style",
            ["Cinematic", "Playful", "Pixel art", "Anime-inspired", "Minimal", "Surprise me"],
        )
    with right:
        if creation_type == "Video":
            detail = st.selectbox("Video length", ["15 seconds", "30 seconds", "60 seconds"])
        else:
            detail = st.selectbox("Game platform", ["Browser (HTML5)", "Mobile", "Desktop"])
    submitted = st.form_submit_button("✨ Generate with AI", use_container_width=True, type="primary")


def get_api_key():
    key = os.getenv("OPENAI_API_KEY", "")
    if not key:
        try:
            key = st.secrets.get("OPENAI_API_KEY", "")
        except (FileNotFoundError, AttributeError):
            pass
    return key.strip()


def build_instructions(kind, description, selected_style, selected_detail):
    if kind == "Video":
        return (
            "You are a skilled video pre-production assistant. Create a practical, original production plan "
            "from the user's idea. Include: a compelling title and logline; a concise visual direction; "
            f"a {selected_detail} storyboard broken into timed shots; camera, lighting, and motion notes; "
            "a narration/dialogue or sound plan; and a polished text-to-video prompt for each shot. "
            "Keep the timing within the requested duration. Do not claim to have rendered or attached a video.\n\n"
            f"Visual style: {selected_style}\nIdea: {description}"
        )
    return (
        "You are an expert indie game designer and web game prototyper. Turn the user's idea into a useful "
        "starter kit. Include: title and one-sentence hook; core gameplay loop; controls; a small first-level "
        "plan; art and audio direction; and a self-contained HTML/CSS/JavaScript prototype when appropriate. "
        "If you provide code, put it in one fenced html code block and keep it simple enough to save as index.html. "
        "Never claim code was tested or executed.\n\n"
        f"Style: {selected_style}\nTarget platform: {selected_detail}\nIdea: {description}"
    )


def extract_html_prototype(text):
    match = re.search(r"```html\s*([\s\S]*?)```", text, re.IGNORECASE)
    return match.group(1).strip() if match else None


if submitted:
    if not prompt.strip():
        st.warning("Add a short description of what you want to create.")
    elif not get_api_key():
        st.error("Add an `OPENAI_API_KEY` environment variable (or Streamlit secret) to enable AI generation.")
        st.code('OPENAI_API_KEY="your-key-here"\nstreamlit run studio_app.py', language="bash")
    else:
        with st.spinner("Dreaming it up…"):
            try:
                response = requests.post(
                    f"{API_URL}/chat/completions",
                    headers={"Authorization": f"Bearer {get_api_key()}"},
                    json={
                        "model": MODEL,
                        "messages": [
                            {"role": "system", "content": "Be imaginative, specific, and easy to follow."},
                            {"role": "user", "content": build_instructions(creation_type, prompt.strip(), style, detail)},
                        ],
                        "temperature": 0.8,
                    },
                    timeout=90,
                )
                response.raise_for_status()
                result = response.json()["choices"][0]["message"]["content"]
                if not isinstance(result, str) or not result.strip():
                    raise ValueError("The AI service returned empty content.")
                st.session_state.latest_creation = {
                    "kind": creation_type,
                    "prompt": prompt.strip(),
                    "style": style,
                    "detail": detail,
                    "result": result.strip(),
                    "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
                }
            except requests.exceptions.HTTPError as error:
                message = "The AI service rejected the request. Check your API key, model access, and account limits."
                try:
                    detail_message = error.response.json().get("error", {}).get("message")
                    if detail_message:
                        message = detail_message
                except (ValueError, AttributeError):
                    pass
                st.error(message)
            except requests.exceptions.RequestException as error:
                st.error(f"Could not reach the AI service: {error}")
            except (KeyError, IndexError, TypeError, ValueError):
                st.error("The AI service returned an unexpected response. Please try again.")

creation = st.session_state.get("latest_creation")
if creation:
    st.subheader("Your creation plan")
    st.caption(f"{creation['kind']} · {creation['created_at']}")
    st.markdown(creation["result"])

    safe_name = re.sub(r"[^a-z0-9]+", "-", creation["prompt"].lower()).strip("-")[:40] or "creation"
    plan_markdown = (
        f"# {creation['kind']} creation plan\n\n"
        f"**Idea:** {creation['prompt']}\n\n"
        f"**Style:** {creation['style']}\n\n"
        f"**Format:** {creation['detail']}\n\n"
        f"**Created:** {creation['created_at']}\n\n---\n\n{creation['result']}\n"
    )
    st.download_button(
        "Download creation plan",
        data=plan_markdown,
        file_name=f"{safe_name}-plan.md",
        mime="text/markdown",
        key="download-plan",
    )

    if creation["kind"] == "Game":
        prototype = extract_html_prototype(creation["result"])
        if prototype:
            st.download_button(
                "Download HTML prototype",
                data=prototype,
                file_name=f"{safe_name}.html",
                mime="text/html",
                key="download-prototype",
            )
            st.info("The HTML file is downloadable but is not executed or previewed on this site. Review generated code before opening it.")
        else:
            st.info("No fenced HTML prototype was included. You can still download the game design plan above.")
    else:
        st.info("This is a storyboard and set of generation prompts—not a rendered video. A video-generation provider can be connected in a next step.")

st.divider()
st.markdown('<p class="note">CreateLab is a starter studio. AI outputs may need review; generated game code is not run on this site.</p>', unsafe_allow_html=True)
