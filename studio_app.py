import os
import re
from datetime import datetime, timezone
from uuid import uuid4

import requests
import streamlit as st

import createlab_auth
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
      .hero h1 { font-size: clamp(2.4rem, 4vw, 4rem); letter-spacing: -.06em; margin: 0; }
      .hero p, .muted { color: #a4a9b8; }
      .eyebrow { color: #a78bfa; text-transform: uppercase; letter-spacing: .16em; font-size: .75rem; font-weight: 700; }
      div[data-testid="stForm"] { border: 1px solid #252938; border-radius: 18px; padding: 1.25rem; background: #11141d; }
      div[data-testid="stMetric"] { background: #11141d; border: 1px solid #252938; padding: 1rem; border-radius: 14px; }
    </style>
    """,
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


def render_auth():
    st.markdown(
        '<div class="hero"><div class="eyebrow">Private creative workspace</div>'
        '<h1>Welcome to <span style="color:#a78bfa">CreateLab.</span></h1>'
        '<p>Sign in or create an account to save and manage your own projects.</p></div>',
        unsafe_allow_html=True,
    )
    tab_login, tab_register = st.tabs(["Sign in", "Create account"])
    with tab_login:
        with st.form("login_form"):
            email = st.text_input("Email", autocomplete="email")
            password = st.text_input("Password", type="password", autocomplete="current-password")
            submitted = st.form_submit_button("Sign in", type="primary", use_container_width=True)
        if submitted:
            user = createlab_auth.authenticate(email, password)
            if user:
                st.session_state.user = user
                st.rerun()
            st.error("Email or password is incorrect.")
    with tab_register:
        with st.form("register_form"):
            name = st.text_input("Display name", max_chars=80, autocomplete="name")
            new_email = st.text_input("Email address", key="register_email", autocomplete="email")
            new_password = st.text_input("Password (at least 12 characters)", type="password", key="register_password", autocomplete="new-password")
            confirm_password = st.text_input("Confirm password", type="password", autocomplete="new-password")
            submitted = st.form_submit_button("Create account", type="primary", use_container_width=True)
        if submitted:
            if new_password != confirm_password:
                st.error("The passwords do not match.")
            else:
                try:
                    user = createlab_auth.register(new_email, name, new_password)
                    st.session_state.user = user
                    st.success("Account created.")
                    st.rerun()
                except ValueError as error:
                    st.error(str(error))
                except Exception:
                    st.error("Could not create the account. Please try again.")


user = st.session_state.get("user")
if user:
    # Refresh the account from the database every rerun. Deleted accounts lose access.
    user = createlab_db.get_user_by_id(user.get("id"))
    if user is None:
        st.session_state.pop("user", None)
        st.rerun()
    st.session_state.user = user

if not st.session_state.get("user"):
    render_auth()
    st.stop()

user = st.session_state.user
counts = createlab_db.creation_counts(user["id"])
if "page" not in st.session_state:
    st.session_state.page = "Create"
if "selected_creation_id" not in st.session_state:
    st.session_state.selected_creation_id = None

with st.sidebar:
    st.markdown("## ✨ CreateLab")
    st.caption(f"Signed in as {user['display_name']}")
    st.radio("Workspace", ["Create", "Dashboard"], key="page")
    if st.button("Sign out", use_container_width=True):
        st.session_state.pop("user", None)
        st.session_state.pop("selected_creation_id", None)
        st.session_state.page = "Create"
        st.rerun()
    st.divider()
    st.caption(f"Configured model: `{MODEL}`")
    st.caption("Projects are private to your account in this database.")
    st.caption("Video outputs are storyboards, not rendered clips. Generated HTML is never executed by this app.")

st.markdown(
    f'<div class="hero"><div class="eyebrow">Creative workspace</div>'
    f'<h1>Make something <span style="color:#a78bfa">unreal.</span></h1>'
    f'<p>Welcome back, {user["display_name"]}. Turn your ideas into video plans and game concepts.</p></div>',
    unsafe_allow_html=True,
)

if st.session_state.page == "Create":
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
                        "id": str(uuid4()), "owner_id": user["id"], "kind": kind,
                        "prompt": prompt.strip(), "style": style, "detail": detail,
                        "result": result.strip(),
                        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    }
                    createlab_db.save_creation(creation)
                    st.session_state.selected_creation_id = creation["id"]
                    st.success("Project generated and saved to your account.")
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

    recent = createlab_db.list_creations(user["id"], limit=5)
    if recent:
        st.divider()
        st.subheader("Your recent projects")
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
    st.subheader("Your project dashboard")
    metric_cols = st.columns(3)
    metric_cols[0].metric("All projects", counts["Video"] + counts["Game"])
    metric_cols[1].metric("Video plans", counts["Video"])
    metric_cols[2].metric("Game projects", counts["Game"])
    filter_kind = st.selectbox("Filter projects", ["All", "Video", "Game"])
    projects = createlab_db.list_creations(user["id"], kind=None if filter_kind == "All" else filter_kind, limit=500)
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
            "Select a saved project", valid_ids, index=index,
            format_func=lambda item_id: labels[item_id], key="dashboard_project_id",
        )
        selected = createlab_db.get_creation(user["id"], chosen_id)
        if selected:
            render_creation(selected)
            if st.button("Delete this project"):
                createlab_db.delete_creation(user["id"], chosen_id)
                st.session_state.selected_creation_id = None
                st.success("Project deleted.")
                st.rerun()

st.divider()
st.caption("Your account and projects are stored in SQLite. This starter does not include email verification, password reset, or multi-factor authentication. Use HTTPS and a persistent database volume for deployment.")
