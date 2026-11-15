import os
import re
from datetime import datetime, timezone
from uuid import uuid4

import requests
import streamlit as st

import createlab_db


API_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

st.set_page_config(page_title="CreateLab — AI Video & Game Studio", page_icon="🎬", layout="wide")
createlab_db.initialize_database()

st.markdown(
    """
    <style>
      .stApp { background: #0b0d13; color: #eef0f6; }
      [data-testid="stSidebar"] { background: #11141d; }
      .hero { padding: 1.4rem 0 .7rem; }
      .hero h1 { font-size: clamp(2.4rem, 5vw, 4rem); letter-spacing: -.06em; margin: 0; }
      .hero p, .muted { color: #a4a9b8; }
      .eyebrow { color: #a78bfa; text-transform: uppercase; letter-spacing: .16em; font-size: .75rem; font-weight: 700; }
      div[data-testid="stForm"] { border: 1px solid #252938; border-radius: 18px; padding: 1.25rem; background: #11141d; }
      div[data-testid="stMetric"] { background: #11141d; border: 1px solid #252938; padding: 1rem; border-radius: 14px; }
    </style>
    """,
    unsafe_allow_html=True,
)

if "page" not in st.session_state:
    st.session_state.page = "Create"
if "selected_creation_id" not in st.session_state:
    st.session_state.selected_creation_id = None

counts = createlab_db.creation_counts()
with st.sidebar:
    st.markdown("## ✨ CreateLab")
    st.caption("AI video planner & game studio")
    page = st.radio("Workspace", ["Create", "Dashboard"], key="page")
    st.divider()
    st.caption(f"Configured model: `{MODEL}`")
    st.caption("Projects are stored in the local SQLite database.")
    st.divider()
    st.caption("Video outputs are storyboards and prompts, not rendered clips. Generated HTML is never executed by this app.")

st.markdown(
    '<div class="hero"><div class="eyebrow">Creative workspace</div>'
    '<h1>Make something <span style="color:#a78bfa">unreal.</span></h1>'
    '<p>Turn your ideas into production-ready video plans and game concepts. Your projects are saved in your local database.</p></div>',
    unsafe_allow_html=True,
)


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
            "You are a skilled video pre-production assistant. Create a practical, original production plan. "
            "Include a compelling title and logline, visual direction, a timed storyboard, camera/lighting/motion notes, "
            "sound or dialogue, and a text-to-video prompt for every shot. Stay within the requested duration; do not claim to render video.\n\n"
            f"Duration: {selected_detail}\nStyle: {selected_style}\nIdea: {description}"
        )
    return (
        "You are an expert indie game designer and web game prototyper. Include a title and hook, gameplay loop, "
        "controls, first level, art/audio direction, and a self-contained HTML/CSS/JavaScript prototype in one fenced html code block. "
        "Keep it simple enough to save as index.html. Do not claim code was tested or executed.\n\n"
        f"Style: {selected_style}\nTarget platform: {selected_detail}\nIdea: {description}"
    )


def extract_html_prototype(text):
    match = re.search(r"```html\s*([\s\S]*?)```", text, re.IGNORECASE)
    return match.group(1).strip() if match else None


def safe_filename(prompt, suffix):
    stem = re.sub(r"[^a-z0-9]+", "-", prompt.lower()).strip("-")[:40] or "creation"
    return f"{stem}{suffix}"


def render_creation(creation):
    st.subheader(creation["kind"] + " project")
    st.caption(f"Created {creation['created_at']} · {creation['style']} · {creation['detail']}")
    st.markdown(f"**Idea:** {creation['prompt']}")
    st.markdown(creation["result"])
    markdown = (
        f"# {creation['kind']} creation plan\n\n**Idea:** {creation['prompt']}\n\n"
        f"**Style:** {creation['style']}\n\n**Format:** {creation['detail']}\n\n"
        f"**Created:** {creation['created_at']}\n\n---\n\n{creation['result']}\n"
    )
    left, right = st.columns(2)
    with left:
        st.download_button(
            "Download plan (Markdown)", markdown,
            file_name=safe_filename(creation["prompt"], "-plan.md"),
            mime="text/markdown", key=f"plan-{creation['id']}",
        )
    prototype = extract_html_prototype(creation["result"]) if creation["kind"] == "Game" else None
    if prototype:
        with right:
            st.download_button(
                "Download HTML prototype", prototype,
                file_name=safe_filename(creation["prompt"], ".html"),
                mime="text/html", key=f"html-{creation['id']}",
            )
        st.info("Review downloaded HTML before opening it. CreateLab does not execute or preview generated code.")
    if creation["kind"] == "Video":
        st.info("This is a storyboard and prompt pack, not a rendered video.")


if page == "Create":
    st.subheader("Start a new project")
    with st.form("creation_form"):
        kind = st.radio("Project type", ["Video", "Game"], horizontal=True)
        prompt = st.text_area(
            "Describe your idea",
            placeholder=("A tiny robot discovers a garden on Mars…" if kind == "Video" else "A fox collects stars in an enchanted forest…"),
            max_chars=2000,
            height=130,
        )
        col_a, col_b = st.columns(2)
        with col_a:
            style = st.selectbox("Style", ["Cinematic", "Playful", "Pixel art", "Anime-inspired", "Minimal", "Surprise me"])
        with col_b:
            detail = st.selectbox("Duration" if kind == "Video" else "Platform", ["15 seconds", "30 seconds", "60 seconds"] if kind == "Video" else ["Browser (HTML5)", "Mobile", "Desktop"])
        submitted = st.form_submit_button("✨ Generate and save project", type="primary", use_container_width=True)

    if submitted:
        if not prompt.strip():
            st.warning("Describe your idea first.")
        elif not get_api_key():
            st.error("Set `OPENAI_API_KEY` in your environment or Streamlit secrets to generate projects.")
            st.code('OPENAI_API_KEY="your-key-here"\nstreamlit run studio_app.py', language="bash")
        else:
            with st.spinner("Creating your project…"):
                try:
                    response = requests.post(
                        f"{API_URL}/chat/completions",
                        headers={"Authorization": f"Bearer {get_api_key()}"},
                        json={
                            "model": MODEL,
                            "messages": [
                                {"role": "system", "content": "Be imaginative, specific, and easy to follow."},
                                {"role": "user", "content": build_instructions(kind, prompt.strip(), style, detail)},
                            ],
                            "temperature": 0.8,
                        },
                        timeout=90,
                    )
                    response.raise_for_status()
                    result = response.json()["choices"][0]["message"]["content"]
                    if not isinstance(result, str) or not result.strip():
                        raise ValueError("The AI service returned empty content.")
                    creation = {
                        "id": str(uuid4()), "kind": kind, "prompt": prompt.strip(), "style": style,
                        "detail": detail, "result": result.strip(),
                        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    }
                    createlab_db.save_creation(creation)
                    st.session_state.selected_creation_id = creation["id"]
                    st.success("Project generated and saved to the database.")
                    render_creation(creation)
                except requests.exceptions.HTTPError as error:
                    message = "The AI service rejected the request. Check the key, model access, and account limits."
                    try:
                        message = error.response.json().get("error", {}).get("message", message)
                    except (ValueError, AttributeError):
                        pass
                    st.error(message)
                except requests.exceptions.RequestException as error:
                    st.error(f"Could not reach the AI service: {error}")
                except (KeyError, IndexError, TypeError, ValueError) as error:
                    st.error(f"Could not save or read the generated response: {error}")

    recent = createlab_db.list_creations(limit=5)
    if recent:
        st.divider()
        st.subheader("Recent projects")
        cols = st.columns(min(len(recent), 3))
        for index, project in enumerate(recent):
            with cols[index % len(cols)]:
                st.markdown(f"**{project['kind']}** · {project['created_at'][:10]}")
                st.caption(project["prompt"][:110] + ("…" if len(project["prompt"]) > 110 else ""))
                if st.button("Open in dashboard", key=f"open-{project['id']}"):
                    st.session_state.selected_creation_id = project["id"]
                    st.session_state.page = "Dashboard"
                    st.rerun()

else:
    st.subheader("Project dashboard")
    metric_cols = st.columns(3)
    metric_cols[0].metric("All projects", counts["Video"] + counts["Game"])
    metric_cols[1].metric("Video plans", counts["Video"])
    metric_cols[2].metric("Game projects", counts["Game"])

    filter_kind = st.selectbox("Filter projects", ["All", "Video", "Game"])
    projects = createlab_db.list_creations(kind=None if filter_kind == "All" else filter_kind, limit=500)
    if not projects:
        st.info("No saved projects yet. Create your first one to see it here.")
        if st.button("Create a project", type="primary"):
            st.session_state.page = "Create"
            st.rerun()
    else:
        labels = {
            item["id"]: f"{item['kind']} · {item['prompt'][:75]}{'…' if len(item['prompt']) > 75 else ''} · {item['created_at'][:10]}"
            for item in projects
        }
        valid_ids = list(labels)
        default_id = st.session_state.get("selected_creation_id")
        index = valid_ids.index(default_id) if default_id in valid_ids else 0
        chosen_id = st.selectbox(
            "Select a saved project", valid_ids,
            index=index, format_func=lambda item_id: labels[item_id], key="dashboard_project_id",
        )
        selected = createlab_db.get_creation(chosen_id)
        if selected:
            render_creation(selected)
            if st.button("Delete this project", type="secondary"):
                createlab_db.delete_creation(chosen_id)
                st.session_state.selected_creation_id = None
                st.success("Project deleted.")
                st.rerun()

st.divider()
st.caption("Projects are stored in SQLite at `CREATELAB_DB_PATH` (default: `data/createlab.sqlite3`). This starter has no user accounts; projects share the configured database.")
