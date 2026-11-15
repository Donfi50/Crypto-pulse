import os
import re
from datetime import datetime, timezone
from uuid import uuid4

import requests
import streamlit as st


API_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
MAX_SAVED_CREATIONS = 10


st.set_page_config(
    page_title="CreateLab — AI Video & Game Studio",
    page_icon="🎬",
    layout="wide",
)

if "creations" not in st.session_state:
    st.session_state.creations = []
if "selected_creation_id" not in st.session_state:
    st.session_state.selected_creation_id = None

st.markdown(
    """
    <style>
      .stApp { background: linear-gradient(180deg, #0b0d13 0%, #101522 100%); color: #eef0f6; }
      [data-testid="stSidebar"] { background: #11141d; }
      .hero { padding: 1.5rem 0 0.8rem; }
      .hero h1 { font-size: clamp(2.5rem, 5vw, 4.5rem); letter-spacing: -0.08em; margin: 0; }
      .hero p { color: #b9c0d4; font-size: 1.08rem; max-width: 760px; }
      .eyebrow { color: #a78bfa; text-transform: uppercase; letter-spacing: .18em; font-size: .72rem; font-weight: 700; }
      .feature-card { background: rgba(17, 20, 29, 0.92); border: 1px solid #2b3145; border-radius: 18px; padding: 1rem; height: 100%; }
      .feature-card h4 { margin-top: 0; }
      div[data-testid="stForm"] { border: 1px solid #252938; border-radius: 18px; padding: 1.25rem; background: #11141d; }
      .note { color: #a4a9b8; font-size: .9rem; }
      .primary-button button { background: linear-gradient(90deg, #6d5efb, #7b9cff); border: none; }
      .small-muted { color: #aeb7cc; font-size: .85rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


st.markdown(
    """
    <div class="hero">
      <div class="eyebrow">Your creative co-pilot</div>
      <h1>Make something <span style="color:#a78bfa">unreal.</span></h1>
      <p>Generate cinematic video plans, game concepts, and playable prototype ideas from a single prompt. Built for creators who want to move from idea to execution faster.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

feature_cols = st.columns(3)
with feature_cols[0]:
    st.markdown(
        """
        <div class="feature-card">
          <h4>🎬 Video planner</h4>
          <div class="small-muted">Storyboard scenes, camera moves, lighting notes, and text-to-video prompts for a polished concept.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with feature_cols[1]:
    st.markdown(
        """
        <div class="feature-card">
          <h4>🎮 Game concept engine</h4>
          <div class="small-muted">Create gameplay loops, level plans, art direction, and starter HTML prototype ideas.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with feature_cols[2]:
    st.markdown(
        """
        <div class="feature-card">
          <h4>📦 Ready to export</h4>
          <div class="small-muted">Download the plan as Markdown and export game HTML blocks when the model provides them.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()

with st.sidebar:
    st.markdown("## CreateLab")
    creation_type = st.radio("What are you making?", ["Video", "Game"], horizontal=True)
    st.divider()
    st.caption("AI settings")
    st.caption(f"Model: `{MODEL}`")
    st.caption("Your API key is read from environment variables or Streamlit secrets.")
    st.divider()
    st.markdown("### Recent creations")
    if st.session_state.creations:
        project_options = {
            item["id"]: f"{item['kind']} · {item['prompt'][:30]}{'…' if len(item['prompt']) > 30 else ''}"
            for item in st.session_state.creations
        }
        selected_id = st.selectbox(
            "Open a recent project",
            options=list(project_options),
            format_func=lambda project_id: project_options[project_id],
            label_visibility="collapsed",
            key="selected_creation_id",
        )
        if st.button("Clear session history", use_container_width=True):
            st.session_state.creations = []
            st.session_state.selected_creation_id = None
            st.rerun()
    else:
        st.caption("Your generated plans will appear here for this session.")
        selected_id = None
    st.divider()
    st.caption("This starter plans content, but it does not render actual videos or run generated game code automatically.")

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
        st.error("Add an `OPENAI_API_KEY` environment variable or Streamlit secret to enable AI generation.")
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
                payload = response.json()
                result = payload["choices"][0]["message"]["content"]
                if not isinstance(result, str) or not result.strip():
                    raise ValueError("The AI service returned empty content.")

                creation = {
                    "id": str(uuid4()),
                    "kind": creation_type,
                    "prompt": prompt.strip(),
                    "style": style,
                    "detail": detail,
                    "result": result.strip(),
                    "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
                }
                st.session_state.creations.insert(0, creation)
                st.session_state.creations = st.session_state.creations[:MAX_SAVED_CREATIONS]
                st.session_state.selected_creation_id = creation["id"]
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

creation = None
if st.session_state.creations:
    selected_id = st.session_state.get("selected_creation_id")
    if selected_id:
        creation = next((item for item in st.session_state.creations if item["id"] == selected_id), None)
    if creation is None:
        creation = st.session_state.creations[0]

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

    col1, col2 = st.columns([1, 1])
    with col1:
        st.download_button(
            "Download creation plan",
            data=plan_markdown,
            file_name=f"{safe_name}-plan.md",
            mime="text/markdown",
            key=f"download-plan-{creation['id']}",
        )

    if creation["kind"] == "Game":
        prototype = extract_html_prototype(creation["result"])
        with col2:
            if prototype:
                st.download_button(
                    "Download HTML prototype",
                    data=prototype,
                    file_name=f"{safe_name}.html",
                    mime="text/html",
                    key=f"download-prototype-{creation['id']}",
                )
            else:
                st.info("No HTML block was included; this plan can still be downloaded.")

    st.info("This is a concept output, not a completed video render or executed game runtime.")

st.divider()
st.markdown('<p class="note">CreateLab is a starter studio. AI outputs may need review. Recent creations are stored only in the active browser session.</p>', unsafe_allow_html=True)

st.markdown(
    """
    <div class="feature-card">
      <strong>Example prompts</strong><br>
      <span class="small-muted">• “A cinematic short about a lonely astronaut who plants the first garden on the moon.”<br>
      • “A cheerful 2D side-scroller where a fox unlocks portals in a glowing forest.”</span>
    </div>
    """,
    unsafe_allow_html=True,
)
