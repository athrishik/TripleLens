import streamlit as st
import time
import concurrent.futures
from datetime import datetime

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="TripleLens",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  GLOBAL CSS  (glassmorphism dark, inspired by
#  the 21st.dev modern-feature-grid aesthetic)
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Root tokens ── */
:root {
    --bg-base:        #0a0a0f;
    --bg-surface:     #0f0f1a;
    --bg-card:        rgba(255,255,255,0.03);
    --bg-card-hover:  rgba(255,255,255,0.06);
    --border:         rgba(255,255,255,0.08);
    --border-hover:   rgba(255,255,255,0.18);
    --text-primary:   #f1f0ff;
    --text-secondary: #9b98b8;
    --text-muted:     #6b6882;
    --purple:         #8B5CF6;
    --purple-glow:    rgba(139,92,246,0.15);
    --gemini:         #4285F4;
    --gemini-glow:    rgba(66,133,244,0.18);
    --llama33:        #F97316;
    --llama33-glow:   rgba(249,115,22,0.18);
    --llama4:         #22D3EE;
    --llama4-glow:    rgba(34,211,238,0.18);
    --radius:         14px;
}

/* ── Base ── */
html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg-base) !important;
    font-family: 'Inter', sans-serif !important;
    color: var(--text-primary) !important;
}

[data-testid="stSidebar"] {
    background: var(--bg-surface) !important;
    border-right: 1px solid var(--border) !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(139,92,246,0.4); border-radius: 99px; }

/* ─── Hero ─── */
.tl-hero {
    text-align: center;
    padding: 2.5rem 0 1.5rem;
    position: relative;
}
.tl-hero::before {
    content: '';
    position: absolute;
    top: -60px; left: 50%;
    transform: translateX(-50%);
    width: 600px; height: 300px;
    background: radial-gradient(ellipse, rgba(139,92,246,0.12) 0%, transparent 70%);
    pointer-events: none;
}
.tl-logo {
    font-size: 2.8rem;
    font-weight: 800;
    letter-spacing: -0.04em;
    background: linear-gradient(135deg, #c4b5fd 0%, #8B5CF6 40%, #22D3EE 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
}
.tl-subtitle {
    font-size: 1rem;
    color: var(--text-secondary);
    margin-top: 0.4rem;
    font-weight: 400;
    letter-spacing: 0.01em;
}

/* ─── Section labels ─── */
.tl-section-label {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 0.5rem;
}

/* ─── Model badge ─── */
.model-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 14px;
    border-radius: 99px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    margin-bottom: 0.9rem;
    border: 1px solid;
}
.badge-gemini  { background: var(--gemini-glow);  color: #93c5fd; border-color: rgba(66,133,244,0.35); }
.badge-llama33 { background: var(--llama33-glow); color: #fdba74; border-color: rgba(249,115,22,0.35); }
.badge-llama4  { background: var(--llama4-glow);  color: #67e8f9; border-color: rgba(34,211,238,0.35); }

/* ─── Response card ─── */
.response-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.2rem 1.3rem;
    min-height: 260px;
    transition: border-color 0.25s, background 0.25s;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    position: relative;
    overflow: hidden;
}
.response-card::before {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: var(--radius);
    pointer-events: none;
    opacity: 0;
    transition: opacity 0.3s;
}
.response-card:hover { border-color: var(--border-hover); background: var(--bg-card-hover); }
.response-card:hover::before { opacity: 1; }

.response-card.gemini-card::before  { background: radial-gradient(ellipse at top left,  var(--gemini-glow),  transparent 60%); }
.response-card.llama33-card::before { background: radial-gradient(ellipse at top left,  var(--llama33-glow), transparent 60%); }
.response-card.llama4-card::before  { background: radial-gradient(ellipse at top left,  var(--llama4-glow),  transparent 60%); }

.response-text {
    font-size: 0.875rem;
    line-height: 1.75;
    color: var(--text-primary);
    white-space: pre-wrap;
    word-break: break-word;
}
.response-text code {
    background: rgba(255,255,255,0.07);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 1px 5px;
    font-size: 0.82em;
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
}

.stats-row {
    display: flex;
    gap: 14px;
    flex-wrap: wrap;
    margin-top: 0.85rem;
    padding-top: 0.85rem;
    border-top: 1px solid var(--border);
}
.stat-chip {
    display: flex;
    align-items: center;
    gap: 5px;
    font-size: 0.7rem;
    color: var(--text-muted);
    font-weight: 500;
}
.stat-chip span.val { color: var(--text-secondary); font-weight: 600; }

/* ─── Placeholder card ─── */
.placeholder-card {
    background: rgba(255,255,255,0.015);
    border: 1px dashed rgba(255,255,255,0.08);
    border-radius: var(--radius);
    padding: 1.2rem 1.3rem;
    min-height: 200px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.6rem;
}
.placeholder-icon { font-size: 1.8rem; filter: grayscale(1); opacity: 0.35; }
.placeholder-text { font-size: 0.8rem; color: var(--text-muted); text-align: center; }

/* ─── Error card ─── */
.error-card {
    background: rgba(239,68,68,0.06);
    border: 1px solid rgba(239,68,68,0.25);
    border-radius: var(--radius);
    padding: 1rem 1.2rem;
}
.error-text { font-size: 0.82rem; color: #fca5a5; }

/* ─── Metrics strip ─── */
.metrics-strip {
    display: grid;
    grid-template-columns: repeat(9, 1fr);
    gap: 0;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    overflow: hidden;
    margin-top: 1.5rem;
}
.metric-cell {
    padding: 1rem 0.8rem;
    text-align: center;
    border-right: 1px solid var(--border);
}
.metric-cell:last-child { border-right: none; }
.metric-label { font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--text-muted); font-weight: 600; margin-bottom: 0.3rem; }
.metric-value { font-size: 1.05rem; font-weight: 700; color: var(--text-primary); }
.metric-sub   { font-size: 0.65rem; color: var(--text-muted); margin-top: 0.1rem; }
.metric-cell.winner .metric-value { color: #a78bfa; }
.metric-section-head {
    grid-column: span 3;
    padding: 0.5rem;
    text-align: center;
    font-size: 0.65rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    font-weight: 700;
    border-bottom: 1px solid var(--border);
    border-right: 1px solid var(--border);
}
.ms-gemini  { color: #93c5fd; background: var(--gemini-glow); }
.ms-llama33 { color: #fdba74; background: var(--llama33-glow); border-right: 1px solid var(--border); }
.ms-llama4  { color: #67e8f9; background: var(--llama4-glow); border-right: none; }

/* ─── Prompt templates ─── */
.template-btn-container {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 0.5rem;
}

/* ─── History item ─── */
.history-item {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.7rem;
}
.history-meta { font-size: 0.7rem; color: var(--text-muted); margin-bottom: 0.4rem; }
.history-prompt { font-size: 0.85rem; color: var(--text-secondary); font-weight: 500; }

/* ─── Sidebar tweaks ─── */
[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] .stTextInput input:focus {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text-primary) !important;
}
[data-testid="stSidebar"] label { color: var(--text-secondary) !important; font-size: 0.8rem !important; }
[data-testid="stSidebar"] .stSlider [data-baseweb="slider"] { margin-top: 0.3rem; }

/* ─── Divider ─── */
.tl-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border), transparent);
    margin: 1.5rem 0;
}

/* ─── Compare button ─── */
.stButton > button {
    background: linear-gradient(135deg, #7C3AED, #8B5CF6) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.02em !important;
    padding: 0.6rem 2rem !important;
    transition: all 0.2s !important;
    box-shadow: 0 4px 20px rgba(139,92,246,0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 28px rgba(139,92,246,0.45) !important;
}

/* ─── Text area / input ─── */
.stTextArea textarea {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
    font-size: 0.9rem !important;
}
.stTextArea textarea:focus {
    border-color: rgba(139,92,246,0.5) !important;
    box-shadow: 0 0 0 3px rgba(139,92,246,0.1) !important;
}

/* ─── Expander ─── */
[data-testid="stExpander"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
}
[data-testid="stExpander"] summary { color: var(--text-secondary) !important; font-size: 0.85rem !important; }

/* ─── st.metric override ─── */
[data-testid="stMetric"] {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 0.8rem 1rem;
}
[data-testid="stMetricValue"] { font-size: 1.1rem !important; color: var(--text-primary) !important; }
[data-testid="stMetricLabel"] { font-size: 0.7rem !important; color: var(--text-muted) !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  SESSION STATE DEFAULTS
# ─────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "prompt_text" not in st.session_state:
    st.session_state.prompt_text = ""


# ─────────────────────────────────────────────
#  API CALL FUNCTIONS
# ─────────────────────────────────────────────
def call_gemini(prompt: str, system: str, key: str, temp: float, max_tok: int) -> dict:
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=key)
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        t0 = time.time()
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=full_prompt,
            config=types.GenerateContentConfig(
                temperature=temp,
                max_output_tokens=max_tok,
            ),
        )
        elapsed = time.time() - t0
        return {
            "text": response.text,
            "tokens_in": response.usage_metadata.prompt_token_count,
            "tokens_out": response.usage_metadata.candidates_token_count,
            "time": elapsed,
            "error": None,
        }
    except Exception as e:
        return {"text": None, "tokens_in": 0, "tokens_out": 0, "time": 0, "error": str(e)}


def call_groq_llama33(prompt: str, system: str, key: str, temp: float, max_tok: int) -> dict:
    try:
        from groq import Groq
        client = Groq(api_key=key)
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        t0 = time.time()
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=max_tok,
            temperature=temp,
            messages=messages,
        )
        elapsed = time.time() - t0
        return {
            "text": response.choices[0].message.content,
            "tokens_in": response.usage.prompt_tokens,
            "tokens_out": response.usage.completion_tokens,
            "time": elapsed,
            "error": None,
        }
    except Exception as e:
        return {"text": None, "tokens_in": 0, "tokens_out": 0, "time": 0, "error": str(e)}


def call_groq_llama4(prompt: str, system: str, key: str, temp: float, max_tok: int) -> dict:
    try:
        from groq import Groq
        client = Groq(api_key=key)
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        t0 = time.time()
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            max_tokens=max_tok,
            temperature=temp,
            messages=messages,
        )
        elapsed = time.time() - t0
        return {
            "text": response.choices[0].message.content,
            "tokens_in": response.usage.prompt_tokens,
            "tokens_out": response.usage.completion_tokens,
            "time": elapsed,
            "error": None,
        }
    except Exception as e:
        return {"text": None, "tokens_in": 0, "tokens_out": 0, "time": 0, "error": str(e)}


# ─────────────────────────────────────────────
#  RENDER HELPERS
# ─────────────────────────────────────────────
MODELS = [
    {
        "id": "gemini",
        "label": "Gemini 3 Flash",
        "provider": "Google",
        "badge_class": "badge-gemini",
        "card_class": "gemini-card",
        "icon": "✦",
        "color": "#4285F4",
    },
    {
        "id": "llama33",
        "label": "Llama 3.3 70B",
        "provider": "Meta · Groq",
        "badge_class": "badge-llama33",
        "card_class": "llama33-card",
        "icon": "⬡",
        "color": "#F97316",
    },
    {
        "id": "llama4",
        "label": "Llama 4 Scout 17B",
        "provider": "Meta · Groq",
        "badge_class": "badge-llama4",
        "card_class": "llama4-card",
        "icon": "◈",
        "color": "#22D3EE",
    },
]

PROMPT_TEMPLATES = [
    ("🧠 Explain Code", "Explain the following code step by step, covering what each part does and why:\n\n```python\ndef fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)\n```"),
    ("✍️ Writing Help", "Help me write a compelling introduction paragraph for an essay about the impact of artificial intelligence on the modern workforce. Make it engaging and thought-provoking."),
    ("📊 Analysis", "Analyze the pros and cons of remote work versus in-office work. Structure your response with clear sections covering productivity, collaboration, work-life balance, and company culture."),
    ("💡 Brainstorm", "Brainstorm 10 innovative startup ideas at the intersection of AI and sustainability. For each idea, give a one-line concept and its core value proposition."),
    ("🔬 Research", "Summarize the current state of research on large language models (LLMs), covering key milestones, architectural innovations, major limitations, and promising future directions."),
]


def render_model_badge(m: dict):
    return f"""
    <div class="model-badge {m['badge_class']}">
        <span>{m['icon']}</span>
        <span>{m['label']}</span>
        <span style="opacity:0.55; font-size:0.65rem; font-weight:400">· {m['provider']}</span>
    </div>
    """


def render_response_card(result: dict | None, m: dict, key_missing: bool):
    if key_missing:
        st.markdown(f"""
        <div class="placeholder-card">
            <div class="placeholder-icon">{m['icon']}</div>
            <div class="placeholder-text">Add a <strong style="color:var(--text-secondary)">{m['provider'].split('·')[0].strip()}</strong> API key in the sidebar to enable this model.</div>
        </div>""", unsafe_allow_html=True)
        return

    if result is None:
        st.markdown(f"""
        <div class="response-card {m['card_class']}">
            <div style="color:var(--text-muted);font-size:0.82rem;text-align:center;padding:3rem 0;">
                Hit <strong style="color:var(--text-secondary)">Compare</strong> to see results here…
            </div>
        </div>""", unsafe_allow_html=True)
        return

    if result["error"]:
        st.markdown(f"""
        <div class="error-card">
            <div style="font-size:0.7rem;font-weight:700;letter-spacing:0.08em;color:#f87171;margin-bottom:0.4rem;">⚠ API ERROR</div>
            <div class="error-text">{result['error']}</div>
        </div>""", unsafe_allow_html=True)
        return

    text = result["text"] or ""
    words = len(text.split())
    stats_html = f"""
    <div class="stats-row">
        <div class="stat-chip">⏱ <span class="val">{result['time']:.2f}s</span></div>
        <div class="stat-chip">↑ <span class="val">{result['tokens_in']:,}</span> in</div>
        <div class="stat-chip">↓ <span class="val">{result['tokens_out']:,}</span> out</div>
        <div class="stat-chip">≡ <span class="val">{words:,}</span> words</div>
    </div>
    """
    # Escape HTML characters in the response text for safe rendering
    safe_text = (text
                 .replace("&", "&amp;")
                 .replace("<", "&lt;")
                 .replace(">", "&gt;"))
    st.markdown(f"""
    <div class="response-card {m['card_class']}">
        <div class="response-text">{safe_text}</div>
        {stats_html}
    </div>""", unsafe_allow_html=True)


def render_metrics_strip(results: dict):
    """Render winner comparison metrics using native st.metric."""
    valid = {k: v for k, v in results.items() if v and not v.get("error")}
    if not valid:
        return

    st.markdown('<div class="tl-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="tl-section-label">⚡ Head-to-Head Metrics</div>', unsafe_allow_html=True)

    col_labels = ["Speed (s)", "Output Tokens", "Word Count"]
    rows = []
    for m in MODELS:
        v = valid.get(m["id"])
        if v:
            rows.append({
                "label": m["label"],
                "speed": round(v["time"], 2),
                "tokens_out": v["tokens_out"],
                "words": len((v["text"] or "").split()),
            })
        else:
            rows.append(None)

    # Build metric columns: 3 models × 3 metrics = 9 cols
    cols = st.columns(9)
    metric_defs = [
        ("Speed", "speed", True),       # lower = better
        ("Out Tokens", "tokens_out", False),
        ("Words", "words", False),
    ]

    col_idx = 0
    for i, m in enumerate(MODELS):
        row = rows[i]
        for label, key, lower_better in metric_defs:
            with cols[col_idx]:
                if row:
                    all_vals = [r[key] for r in rows if r]
                    if lower_better:
                        best = min(all_vals)
                        delta_dir = "off"
                        delta = None
                    else:
                        best = max(all_vals)
                        delta_dir = "normal"
                        delta = None

                    is_winner = row[key] == best
                    val = row[key]
                    display = f"{val:.2f}" if isinstance(val, float) else f"{val:,}"
                    st.metric(
                        label=f"{'🏆 ' if is_winner else ''}{label}",
                        value=display,
                    )
                else:
                    st.metric(label=label, value="—")
            col_idx += 1


# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:1rem 0 0.5rem">
        <div style="font-size:1.15rem;font-weight:700;color:#c4b5fd;letter-spacing:-0.02em">🔍 TripleLens</div>
        <div style="font-size:0.72rem;color:var(--text-muted);margin-top:0.2rem">AI Model Comparison</div>
    </div>
    <div class="tl-divider" style="margin:0.8rem 0"></div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="tl-section-label">🔑 API Keys</div>', unsafe_allow_html=True)
    gemini_key = st.text_input(
        "Gemini API Key",
        type="password",
        placeholder="AIza...",
        help="Get a free key at aistudio.google.com",
    )
    groq_key = st.text_input(
        "Groq API Key",
        type="password",
        placeholder="gsk_...",
        help="Get a free key at console.groq.com — covers both Llama models",
    )

    st.markdown('<div class="tl-divider" style="margin:1rem 0"></div>', unsafe_allow_html=True)
    st.markdown('<div class="tl-section-label">⚙ Generation</div>', unsafe_allow_html=True)

    temperature = st.slider(
        "Temperature",
        min_value=0.0, max_value=1.0,
        value=0.7, step=0.05,
        help="Higher = more creative; lower = more deterministic",
    )
    max_tokens = st.slider(
        "Max Output Tokens",
        min_value=100, max_value=4000,
        value=1024, step=100,
    )

    st.markdown('<div class="tl-divider" style="margin:1rem 0"></div>', unsafe_allow_html=True)
    st.markdown('<div class="tl-section-label">ℹ Models Active</div>', unsafe_allow_html=True)

    for m in MODELS:
        has_key = bool(gemini_key) if m["id"] == "gemini" else bool(groq_key)
        dot = "🟢" if has_key else "⚪"
        st.markdown(
            f'<div style="font-size:0.78rem;color:var(--text-secondary);padding:2px 0">'
            f'{dot} {m["label"]}</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div style="margin-top:auto;padding-top:2rem;font-size:0.65rem;color:var(--text-muted);line-height:1.6">'
        'Responses run in parallel. API keys are never stored.<br>'
        'Models: Gemini 3 Flash · Llama 3.3 70B · Llama 4 Scout 17B'
        '</div>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
#  MAIN AREA
# ─────────────────────────────────────────────
st.markdown("""
<div class="tl-hero">
    <div class="tl-logo">🔍 TripleLens</div>
    <div class="tl-subtitle">Compare three frontier AI models, side by side, in real time.</div>
</div>
""", unsafe_allow_html=True)

# ── Prompt templates ──
with st.expander("✨ Prompt Templates", expanded=False):
    st.markdown('<div style="font-size:0.78rem;color:var(--text-muted);margin-bottom:0.6rem">Click any template to load it into the prompt field.</div>', unsafe_allow_html=True)
    tcols = st.columns(5)
    for i, (label, tpl) in enumerate(PROMPT_TEMPLATES):
        with tcols[i]:
            if st.button(label, key=f"tpl_{i}", use_container_width=True):
                st.session_state.prompt_text = tpl
                st.rerun()

# ── System prompt ──
with st.expander("🛠 System Prompt (optional)", expanded=False):
    system_prompt = st.text_area(
        "System instructions applied to all models",
        placeholder="e.g. You are a concise, expert-level technical writer. Always respond in markdown.",
        height=80,
        label_visibility="collapsed",
    )

# ── Main prompt ──
st.markdown('<div class="tl-section-label" style="margin-top:1rem">Your Prompt</div>', unsafe_allow_html=True)
user_prompt = st.text_area(
    "prompt",
    value=st.session_state.prompt_text,
    placeholder="Ask anything — a question, a task, a creative brief…",
    height=130,
    label_visibility="collapsed",
    key="main_prompt",
)

left, _, right = st.columns([2, 6, 2])
with left:
    compare_btn = st.button("⚡ Compare", use_container_width=True)
with right:
    if st.button("🗑 Clear", use_container_width=True):
        st.session_state.prompt_text = ""
        st.rerun()


# ─────────────────────────────────────────────
#  RESULTS
# ─────────────────────────────────────────────
st.markdown('<div class="tl-divider" style="margin:1.2rem 0"></div>', unsafe_allow_html=True)

results: dict[str, dict | None] = {m["id"]: None for m in MODELS}
key_map = {
    "gemini":  bool(gemini_key),
    "llama33": bool(groq_key),
    "llama4":  bool(groq_key),
}

if compare_btn and user_prompt.strip():
    # Build tasks for models that have keys
    tasks = {}
    if gemini_key:
        tasks["gemini"] = (call_gemini, user_prompt, system_prompt or "", gemini_key, temperature, max_tokens)
    if groq_key:
        tasks["llama33"] = (call_groq_llama33, user_prompt, system_prompt or "", groq_key, temperature, max_tokens)
        tasks["llama4"]  = (call_groq_llama4,  user_prompt, system_prompt or "", groq_key, temperature, max_tokens)

    if not tasks:
        st.warning("⚠ Add at least one API key in the sidebar to run a comparison.", icon="🔑")
    else:
        with st.spinner("Running parallel inference across models…"):
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                futures = {
                    model_id: executor.submit(fn, *args)
                    for model_id, (fn, *args) in tasks.items()
                }
                for model_id, future in futures.items():
                    results[model_id] = future.result()

        # Save to history
        st.session_state.history.append({
            "ts": datetime.now().strftime("%H:%M:%S"),
            "prompt": user_prompt[:120] + ("…" if len(user_prompt) > 120 else ""),
            "results": {k: v for k, v in results.items() if v},
        })

# ── 3-column response layout ──
col1, col2, col3 = st.columns(3, gap="small")
cols = [col1, col2, col3]

for i, m in enumerate(MODELS):
    with cols[i]:
        st.markdown(render_model_badge(m), unsafe_allow_html=True)
        render_response_card(results[m["id"]], m, not key_map[m["id"]])

# ── Metrics strip ──
if any(results[m["id"]] and not results[m["id"]].get("error") for m in MODELS):
    render_metrics_strip(results)


# ─────────────────────────────────────────────
#  SESSION HISTORY
# ─────────────────────────────────────────────
if st.session_state.history:
    st.markdown('<div class="tl-divider" style="margin-top:2rem"></div>', unsafe_allow_html=True)
    with st.expander(f"📋 Session History  ({len(st.session_state.history)} queries)", expanded=False):
        for entry in reversed(st.session_state.history):
            st.markdown(f"""
            <div class="history-item">
                <div class="history-meta">🕐 {entry['ts']} · {len(entry['results'])} model(s)</div>
                <div class="history-prompt">{entry['prompt']}</div>
            </div>""", unsafe_allow_html=True)
