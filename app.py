"""
NEXUS.AI | Media Intelligence
==============================
A premium, cyberpunk-glass Streamlit frontend for the AI Video & Meeting
Assistant (Whisper + Mistral AI + ChromaDB + LangChain backend).

WIRE-UP
-------
This file expects two functions from your backend:
    run_pipeline(source: str, language: str) -> dict
    ask_question(rag_chain, question: str) -> str

Update the import block below to point at wherever those live in your
project (e.g. `from main import run_pipeline, ask_question`).

Run with:  streamlit run app.py
Requires:  streamlit >= 1.40 (uses st.segmented_control, st.container(height=...))
"""

import html
import os
import re
import tempfile

import streamlit as st

# ── Backend pipeline ────────────────────────────────────────────────────
# ⚠️ Update this import to match your project structure. Backend logic
# itself is untouched — this file only calls these two functions.
try:
    from main import run_pipeline, ask_question
except ImportError:
    run_pipeline = None
    ask_question = None


# ── Page config ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Nexus.ai | Media Intelligence",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ── Styling ────────────────────────────────────────────────────────────
# All selectors below were verified against Streamlit 1.61's live DOM
# (react-aria based widgets) rather than assumed from older docs/snippets.
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500;700&display=swap');

:root {
    --bg-primary: #0b0f19;
    --bg-secondary: #10151f;
    --glass-bg: rgba(255, 255, 255, 0.035);
    --glass-border: rgba(255, 255, 255, 0.09);
    --accent-purple: #9B6BFF;
    --accent-cyan: #22D3EE;
    --accent-blue: #4C8DFF;
    --accent-amber: #F5B942;
    --text-primary: #E8EBF2;
    --text-secondary: #8891A7;
    --text-muted: #5B6479;
    --brand-gradient: linear-gradient(135deg, var(--accent-purple), var(--accent-cyan));
}

/* ── Base ─────────────────────────────────────────────────────────── */
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
h1, h2, h3 { font-family: 'Space Grotesk', sans-serif !important; }

.stApp {
    background:
        radial-gradient(circle at 15% -10%, rgba(155, 107, 255, 0.12), transparent 40%),
        radial-gradient(circle at 90% 5%, rgba(34, 211, 238, 0.09), transparent 35%),
        var(--bg-primary);
}

/* ── Chrome: hide ONLY the deploy button / main menu / footer.       │
   NEVER hide [data-testid="stToolbar"] wholesale — the sidebar's     │
   expand/collapse controls live inside it in current Streamlit, so   │
   hiding the toolbar makes the sidebar unrecoverable once closed. ─ */
footer { visibility: hidden; }
[data-testid="stToolbarActions"] { display: none !important; }
[data-testid="stAppDeployButton"] { display: none !important; }
[data-testid="stMainMenu"] { display: none !important; }
[data-testid="stHeader"] { background: transparent; }

/* Sidebar collapse / expand controls — ALWAYS visible, neon accent.
   Covers both the current testid (stExpandSidebarButton, the button
   inside the sidebar itself) and the legacy collapsedControl testid
   some Streamlit versions use, so this survives version differences. */
[data-testid="stExpandSidebarButton"],
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapseButton"],
button[data-testid="stBaseButton-headerNoPadding"] {
    visibility: visible !important;
    opacity: 1 !important;
    background: rgba(34, 211, 238, 0.12) !important;
    border: 1px solid rgba(34, 211, 238, 0.45) !important;
    border-radius: 8px !important;
}
[data-testid="stExpandSidebarButton"] *,
[data-testid="collapsedControl"] *,
button[data-testid="stBaseButton-headerNoPadding"] * {
    color: var(--accent-cyan) !important;
    fill: var(--accent-cyan) !important;
}

/* ── Scrollbar ────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--brand-gradient); border-radius: 8px; }

/* ── Signature signal bar ────────────────────────────────────────── */
.signal-bar {
    height: 3px;
    width: 100%;
    background: linear-gradient(90deg, var(--accent-purple), var(--accent-cyan), var(--accent-blue), var(--accent-purple));
    background-size: 300% 100%;
    animation: signal-flow 6s linear infinite;
    border-radius: 2px;
    margin-bottom: 1.75rem;
}
@keyframes signal-flow {
    0% { background-position: 0% 50%; }
    100% { background-position: 300% 50%; }
}
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

/* ── Glassmorphism card ──────────────────────────────────────────── */
.glass-card {
    background: var(--glass-bg);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid var(--glass-border);
    border-radius: 18px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35);
    animation: fadeInUp 0.5s ease both;
}

/* ── Hero card ────────────────────────────────────────────────────── */
.hero-card {
    border-radius: 20px;
    padding: 1.5px;
    background: var(--brand-gradient);
    margin-bottom: 1.5rem;
    animation: fadeInUp 0.5s ease both;
}
.hero-card-inner { background: var(--bg-secondary); border-radius: 18.5px; padding: 1.75rem 2rem; }
.hero-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.15em;
    color: var(--accent-cyan);
    margin-bottom: 0.5rem;
}
.hero-title { font-family: 'Space Grotesk', sans-serif; font-size: 1.7rem; font-weight: 700; color: var(--text-primary); line-height: 1.3; }
.hero-source-pill {
    display: inline-block;
    margin-top: 0.75rem;
    padding: 0.25rem 0.7rem;
    border-radius: 999px;
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    font-size: 0.72rem;
    color: var(--text-secondary);
    font-family: 'JetBrains Mono', monospace;
}

/* ── Stat cards (glassmorphism metrics) ──────────────────────────── */
.stat-card { text-align: center; padding: 1.25rem 0.5rem; }
.stat-icon { font-size: 1.3rem; margin-bottom: 0.35rem; }
.stat-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.9rem;
    font-weight: 700;
    background: var(--brand-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.stat-label { font-size: 0.72rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.07em; margin-top: 0.2rem; }

/* ── Content / list cards ─────────────────────────────────────────── */
.content-card { padding: 1.75rem 2rem; color: var(--text-primary); font-size: 0.98rem; line-height: 1.7; }
.list-card { padding: 0.25rem 1.5rem; }
.list-item { display: flex; gap: 0.9rem; align-items: flex-start; padding: 0.9rem 0; border-bottom: 1px solid var(--glass-border); }
.list-item:last-child { border-bottom: none; }
.list-item-marker { font-family: 'JetBrains Mono', monospace; font-size: 0.95rem; color: var(--accent-cyan); min-width: 1.2rem; }
.decision-item .list-item-marker { color: var(--accent-purple); }
.question-item .list-item-marker { color: var(--accent-amber); }
.list-item-text { color: var(--text-primary); font-size: 0.95rem; line-height: 1.55; }
.empty-tab { text-align: center; color: var(--text-secondary); padding: 2.5rem 1rem; }

/* ── Empty state ──────────────────────────────────────────────────── */
.empty-state { text-align: center; padding: 4rem 2rem; margin-top: 1rem; }
.empty-state-icon { font-size: 3rem; margin-bottom: 1rem; }
.empty-state-title { font-family: 'Space Grotesk', sans-serif; font-size: 1.4rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.6rem; }
.empty-state-desc { color: var(--text-secondary); font-size: 0.95rem; max-width: 420px; margin: 0 auto; line-height: 1.6; }

/* ── Chat ─────────────────────────────────────────────────────────── */
.chat-hint { color: var(--text-secondary); font-size: 0.85rem; margin-bottom: 1rem; }
[data-testid="stChatMessage"] { background: var(--glass-bg); border: 1px solid var(--glass-border); border-radius: 14px; margin-bottom: 0.6rem; }
.stChatInput * { background: transparent; }
.stChatInput { background: var(--glass-bg) !important; border: 1px solid var(--glass-border) !important; border-radius: 16px !important; }
.stChatInput textarea { color: var(--text-primary) !important; }
.stChatInput textarea::placeholder { color: var(--text-muted) !important; }
[data-testid="stChatInputSubmitButton"] { background: var(--brand-gradient) !important; border-radius: 50% !important; }

/* ── Sidebar ──────────────────────────────────────────────────────── */
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0d1220 0%, #0a0e17 100%); border-right: 1px solid var(--glass-border); }
[data-testid="stSidebar"] .block-container { padding-top: 2rem; }

.sidebar-logo { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.25rem; }
.sidebar-logo-icon { font-size: 2rem; }
.sidebar-logo-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.25rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    background: var(--brand-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.1;
}
.sidebar-logo-subtitle { font-size: 0.66rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.05em; }
.sidebar-section-label { font-size: 0.72rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.08em; margin: 1rem 0 0.5rem 0; font-weight: 600; }
.how-it-works-step { display: flex; gap: 0.75rem; margin-bottom: 0.9rem; }
.step-number { font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: var(--accent-cyan); font-weight: 700; padding-top: 0.15rem; }
.step-title { font-size: 0.82rem; font-weight: 600; color: var(--text-primary); }
.step-desc { font-size: 0.74rem; color: var(--text-secondary); line-height: 1.4; }
.sidebar-footer { font-size: 0.68rem; color: var(--text-muted); text-align: center; margin-top: 1.5rem; letter-spacing: 0.03em; }

/* ── Text inputs / select ─────────────────────────────────────────── */
/* Streamlit wraps inputs in a react-aria field with its own opaque
   background div one level down; neutralize it and paint the field. */
.stTextInput div, .stSelectbox div, .stTextArea div { background: transparent !important; border: none !important; box-shadow: none !important; }
.stTextInput input, .stSelectbox input, .stTextArea textarea {
    background: #131826 !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
}
.stTextInput input:focus, .stSelectbox input:focus, .stTextArea textarea:focus {
    border-color: var(--accent-cyan) !important;
    box-shadow: 0 0 0 1px var(--accent-cyan) !important;
    outline: none !important;
}
.stTextInput input::placeholder { color: var(--text-muted) !important; }
/* Kill Streamlit's default red focus/outline ring wherever it can appear
   (text fields, comboboxes, chat input) so only our cyan ring shows. */
.stTextInput, .stSelectbox, .stChatInput,
.stTextInput *, .stSelectbox *, .stChatInput * {
    outline: none !important;
}
.stChatInput:focus-within {
    border-color: var(--accent-cyan) !important;
    box-shadow: 0 0 0 1px var(--accent-cyan) !important;
}

/* Selectbox / combobox dropdown popover (rendered in a portal) */
[role="listbox"] { background: var(--bg-secondary) !important; border: 1px solid var(--glass-border) !important; border-radius: 12px !important; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5) !important; }
[role="listbox"] [role="option"] { color: var(--text-primary) !important; border-radius: 8px !important; }
[role="listbox"] [role="option"][data-focused="true"],
[role="listbox"] [role="option"][aria-selected="true"] {
    background: linear-gradient(135deg, rgba(155, 107, 255, 0.25), rgba(34, 211, 238, 0.25)) !important;
}

/* File uploader */
[data-testid="stFileUploaderDropzone"] { background: var(--glass-bg) !important; border: 1.5px dashed var(--glass-border) !important; border-radius: 14px !important; }
[data-testid="stFileUploaderDropzone"] button { background: var(--glass-bg) !important; border: 1px solid var(--glass-border) !important; color: var(--text-primary) !important; border-radius: 8px !important; }

/* Segmented control (source picker: YouTube URL vs Upload File) */
[data-testid="stButtonGroup"] [role="radiogroup"] { background: var(--glass-bg); border: 1px solid var(--glass-border); border-radius: 12px; padding: 4px; gap: 4px; }
[data-testid="stButtonGroup"] button { background: transparent !important; border: none !important; color: var(--text-secondary) !important; border-radius: 9px !important; }
[data-testid="stButtonGroup"] button[data-selected="true"] { background: var(--brand-gradient) !important; color: #0b0f19 !important; font-weight: 600; }

/* ── Buttons ──────────────────────────────────────────────────────── */
.stButton > button {
    background: var(--brand-gradient);
    color: #0b0f19;
    font-weight: 700;
    border: none;
    border-radius: 12px;
    padding: 0.6rem 1.4rem;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    box-shadow: 0 4px 20px rgba(155, 107, 255, 0.25), 0 4px 20px rgba(34, 211, 238, 0.15);
}
.stButton > button:hover {
    transform: translateY(-2px) scale(1.03);
    box-shadow: 0 8px 28px rgba(155, 107, 255, 0.45), 0 8px 28px rgba(34, 211, 238, 0.3);
    color: #0b0f19;
}
.stButton > button:active { transform: translateY(0) scale(1.0); }

/* ── Tabs ─────────────────────────────────────────────────────────── */
[role="tablist"] { gap: 4px; background: var(--glass-bg); padding: 6px; border-radius: 14px; border: 1px solid var(--glass-border); }
[data-testid="stTab"] { border-radius: 10px; padding: 8px 18px; color: var(--text-secondary); }
[data-testid="stTab"] p { font-size: 0.92rem; font-weight: 500; }
[data-testid="stTab"][data-selected="true"] {
    background: linear-gradient(135deg, rgba(155, 107, 255, 0.22), rgba(34, 211, 238, 0.22)) !important;
    color: var(--text-primary) !important;
}
.react-aria-SelectionIndicator { background: var(--brand-gradient) !important; }
"""

st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)


# ── Helpers ──────────────────────────────────────────────────────────────
def safe_html(text: str) -> str:
    """Escape text before dropping it into a raw HTML block, preserving line breaks."""
    return html.escape(str(text)).replace("\n", "<br>")


def normalize_to_list(content) -> list:
    """Backend fields may come back as a list or as a newline/bulleted string — normalize either into a clean list."""
    if not content:
        return []
    if isinstance(content, list):
        return [str(item).strip() for item in content if str(item).strip()]
    text = str(content).strip()
    cleaned = []
    for line in text.split("\n"):
        line = line.strip().lstrip("-•*").strip()
        line = re.sub(r"^\d+[\.\)]\s*", "", line)
        if line:
            cleaned.append(line)
    return cleaned if cleaned else [text]


def word_count(text) -> int:
    return len(str(text).split()) if text else 0


def save_uploaded_file(uploaded_file) -> str:
    """Persist an uploaded file to a temp path and return it, since run_pipeline expects a source path/URL."""
    temp_path = os.path.join(tempfile.gettempdir(), uploaded_file.name)
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return temp_path


# ── Render helpers ─────────────────────────────────────────────────────
def render_empty_state():
    st.markdown(
        '<div class="empty-state glass-card">'
        '<div class="empty-state-icon">🛰️</div>'
        '<div class="empty-state-title">No signal yet</div>'
        '<div class="empty-state-desc">Drop a YouTube link or upload a recording in the sidebar, '
        "then hit <b>Analyze Meeting</b> to get your summary, action items, decisions, "
        "and a chat-ready assistant.</div></div>",
        unsafe_allow_html=True,
    )


def render_list_tab(items: list, kind: str, empty_message: str):
    if not items:
        st.markdown(f'<div class="glass-card empty-tab">{empty_message}</div>', unsafe_allow_html=True)
        return

    icon_map = {"action": "☐", "decision": "◆", "question": "?"}
    icon = icon_map.get(kind, "•")

    # NOTE: built as single-line strings with no leading indentation.
    # Multi-line indented HTML here would trip Streamlit's markdown parser
    # into rendering it as a literal code block instead of HTML.
    items_html = "".join(
        f'<div class="list-item {kind}-item"><div class="list-item-marker">{icon}</div>'
        f'<div class="list-item-text">{safe_html(item)}</div></div>'
        for item in items
    )
    st.markdown(f'<div class="glass-card list-card">{items_html}</div>', unsafe_allow_html=True)


def render_chat_tab(rag_chain):
    if rag_chain is None:
        st.markdown('<div class="glass-card empty-tab">Chat isn\'t available for this meeting.</div>', unsafe_allow_html=True)
        return

    st.markdown(
        '<div class="chat-hint">Ask anything about this meeting — answers are grounded in the transcript.</div>',
        unsafe_allow_html=True,
    )

    chat_box = st.container(height=420)
    with chat_box:
        if not st.session_state.messages:
            st.markdown('<div class="empty-tab">Start the conversation below 👇</div>', unsafe_allow_html=True)
        for msg in st.session_state.messages:
            avatar = "🧑" if msg["role"] == "user" else "🌌"
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"])

    question = st.chat_input("Ask a question about the meeting...")
    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.spinner("⚡ Retrieving context and thinking..."):
            try:
                answer = ask_question(rag_chain, question)
            except Exception as exc:
                answer = f"⚠️ Something went wrong answering that: {exc}"
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.rerun()


def render_results(result: dict):
    action_items = normalize_to_list(result.get("action_items"))
    decisions = normalize_to_list(result.get("key_decisions"))
    questions = normalize_to_list(result.get("open_questions"))
    transcript_words = word_count(result.get("transcript"))

    source_pill = (
        f'<div class="hero-source-pill">📡 {safe_html(st.session_state.source_label)}</div>'
        if st.session_state.source_label
        else ""
    )

    st.markdown(
        f'<div class="hero-card"><div class="hero-card-inner">'
        f'<div class="hero-eyebrow">MEETING BRIEFING</div>'
        f'<div class="hero-title">{safe_html(result.get("title") or "Untitled Meeting")}</div>'
        f"{source_pill}</div></div>",
        unsafe_allow_html=True,
    )

    stat_cols = st.columns(4)
    stats = [
        ("✅", len(action_items), "Action Items"),
        ("🔑", len(decisions), "Key Decisions"),
        ("❓", len(questions), "Open Questions"),
        ("📄", f"{transcript_words:,}", "Transcript Words"),
    ]
    for col, (icon, value, label) in zip(stat_cols, stats):
        with col:
            st.markdown(
                f'<div class="stat-card glass-card"><div class="stat-icon">{icon}</div>'
                f'<div class="stat-value">{value}</div><div class="stat-label">{label}</div></div>',
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    tab_summary, tab_actions, tab_decisions, tab_questions, tab_chat = st.tabs(
        ["📝 Summary", "✅ Action Items", "🔑 Key Decisions", "❓ Open Questions", "💬 Chat"]
    )

    with tab_summary:
        summary_text = result.get("summary") or "No summary available."
        st.markdown(f'<div class="glass-card content-card">{safe_html(summary_text)}</div>', unsafe_allow_html=True)

    with tab_actions:
        render_list_tab(action_items, "action", "No action items were identified in this meeting.")

    with tab_decisions:
        render_list_tab(decisions, "decision", "No key decisions were identified in this meeting.")

    with tab_questions:
        render_list_tab(questions, "question", "No open questions were identified in this meeting.")

    with tab_chat:
        render_chat_tab(result.get("rag_chain"))


# ── Session state ──────────────────────────────────────────────────────
if "result" not in st.session_state:
    st.session_state.result = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "source_label" not in st.session_state:
    st.session_state.source_label = ""


# ── Sidebar ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div class="sidebar-logo"><div class="sidebar-logo-icon">🌌</div><div>'
        '<div class="sidebar-logo-title">NEXUS.AI</div>'
        '<div class="sidebar-logo-subtitle">Media Intelligence</div></div></div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="sidebar-section-label">Source</div>', unsafe_allow_html=True)
    input_method = st.segmented_control(
        "Input method",
        ["🔗 YouTube URL", "📁 Upload File"],
        default="🔗 YouTube URL",
        label_visibility="collapsed",
    )
    if input_method is None:  # segmented_control allows deselecting; fall back to a sane default
        input_method = "🔗 YouTube URL"

    source = None
    pending_label = ""
    if input_method == "🔗 YouTube URL":
        url_value = st.text_input("YouTube URL", placeholder="https://youtube.com/watch?v=...", label_visibility="collapsed")
        if url_value:
            source = url_value.strip()
            pending_label = "YouTube"
    else:
        uploaded = st.file_uploader("Upload recording", type=["mp4", "mp3", "wav", "m4a", "mov"], label_visibility="collapsed")
        if uploaded is not None:
            source = save_uploaded_file(uploaded)
            pending_label = uploaded.name

    st.markdown('<div class="sidebar-section-label">Language</div>', unsafe_allow_html=True)
    language = st.selectbox("Language", ["english", "hinglish"], label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)
    analyze_clicked = st.button("⚡  Analyze Meeting", use_container_width=True)

    st.markdown("---")
    st.markdown('<div class="sidebar-section-label">How it works</div>', unsafe_allow_html=True)
    for num, title, desc in [
        ("01", "Drop a link or file", "Paste a YouTube URL or upload a recording."),
        ("02", "AI transcribes it", "Whisper converts speech to text, chunk by chunk."),
        ("03", "Insights get extracted", "Summary, decisions, action items, and questions."),
        ("04", "Ask it anything", "Chat with the meeting using RAG-powered retrieval."),
    ]:
        st.markdown(
            f'<div class="how-it-works-step"><div class="step-number">{num}</div><div>'
            f'<div class="step-title">{title}</div><div class="step-desc">{desc}</div></div></div>',
            unsafe_allow_html=True,
        )

    if st.session_state.result is not None:
        st.markdown("---")
        if st.button("🔄  New Analysis", use_container_width=True):
            st.session_state.result = None
            st.session_state.messages = []
            st.session_state.source_label = ""
            st.rerun()

    st.markdown('<div class="sidebar-footer">Powered by LangChain · Mistral AI · ChromaDB</div>', unsafe_allow_html=True)


# ── Processing ─────────────────────────────────────────────────────────
if analyze_clicked:
    if run_pipeline is None:
        st.toast("⚠️ Backend not connected — check the import at the top of app.py.", icon="⚠️")
    elif not source:
        st.toast("⚠️ Please provide a YouTube URL or upload a file first.", icon="⚠️")
    else:
        try:
            with st.spinner("⚡ Transcribing and analyzing your meeting — this can take a few minutes..."):
                result = run_pipeline(source, language)
            st.session_state.result = result
            st.session_state.messages = []
            st.session_state.source_label = pending_label
            st.toast("Analysis complete!", icon="✅")
            st.rerun()
        except Exception as exc:
            st.error(f"Something went wrong while processing this meeting: {exc}")


# ── Main area ─────────────────────────────────────────────────────────
st.markdown('<div class="signal-bar"></div>', unsafe_allow_html=True)

if run_pipeline is None:
    st.error(
        "Backend functions `run_pipeline` / `ask_question` couldn't be imported. "
        "Update the import at the top of app.py to point at your backend module."
    )
elif st.session_state.result is None:
    render_empty_state()
else:
    render_results(st.session_state.result)