import streamlit as st
import time
import html  # BUG 3 FIX: needed for html.escape() to prevent model output from breaking card HTML
import concurrent.futures
from datetime import datetime

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TripleLensLearning",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Fira+Code:wght@400;500&display=swap');

:root {
  --gemini:       #4285F4;
  --llama33:      #F97316;
  --llama4:       #22D3EE;
  --accent:       #8B5CF6;
  --green-prompt: #4ADE80;
  --bg:           #080B10;
  --bg-card:      #0E1117;
  --bg-raised:    #141921;
  --border:       rgba(255,255,255,0.07);
  --border-h:     rgba(255,255,255,0.13);
  --text-1:       #EEF2FF;
  --text-2:       #8892B0;
  --text-3:       #4A5568;
  --r-sm: 8px; --r-md: 12px; --r-lg: 18px;
  --font:  'Outfit', sans-serif;
  --mono:  'Fira Code', monospace;
}

html, body, [class*="css"] { font-family: var(--font) !important; color: var(--text-1); }

.stApp {
  background: var(--bg) !important;
  background-image:
    radial-gradient(ellipse 110% 60% at 0% -5%,   rgba(139,92,246,0.11) 0%, transparent 55%),
    radial-gradient(ellipse  70% 50% at 100% 110%, rgba(34,211,238,0.08) 0%, transparent 55%),
    radial-gradient(ellipse  50% 40% at 50%  50%,  rgba(66,133,244,0.04) 0%, transparent 65%);
  background-attachment: fixed;
}
.block-container { padding-top: 0 !important; max-width: 1440px !important; width: 100% !important; margin-left: auto !important; margin-right: auto !important; }
#MainMenu, footer { visibility: hidden; }
/* ── SIDEBAR FIX: Never hide the whole header — that kills the sidebar expand button's
   pointer events in Chromium even when visibility:visible is re-applied on the child.
   Instead, hide only the specific toolbar elements inside the header. ── */
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
[data-testid="stStatusWidget"] { display: none !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
  background: #09090F !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] > div:first-child { padding-top: 0 !important; }

.sb-brand {
  padding: 1.5rem 1.1rem 1.3rem;
  border-bottom: 1px solid var(--border);
  margin-bottom: 1.3rem;
}
.sb-brand .logo-row { display:flex; align-items:center; gap:0.6rem; margin-bottom:0.3rem; }
.sb-brand .logo-box {
  width:34px; height:34px;
  background: linear-gradient(135deg,#8B5CF6,#22D3EE);
  border-radius: 9px;
  display:flex; align-items:center; justify-content:center;
  font-size:1rem; flex-shrink:0;
}
.sb-brand h2 { font-size:1rem !important; font-weight:700 !important; color:var(--text-1) !important; letter-spacing:-0.02em; margin:0 !important; }
.sb-brand p  { font-size:0.65rem !important; color:var(--text-3) !important; margin:0 !important; text-transform:uppercase; letter-spacing:0.1em; }

.sb-section {
  font-size:0.6rem; font-weight:600; text-transform:uppercase; letter-spacing:0.14em;
  color:var(--text-3); margin:0 0 0.55rem;
  display:flex; align-items:center; gap:0.4rem;
}
.sb-section::after { content:''; flex:1; height:1px; background:var(--border); }

.model-list { display:flex; flex-direction:column; gap:0.35rem; padding-bottom:0.6rem; }
.model-pill {
  display:flex; align-items:center; gap:0.5rem;
  background:var(--bg-raised); border:1px solid var(--border);
  border-radius:8px; padding:0.4rem 0.65rem; font-size:0.71rem; color:var(--text-2);
}
.mp-dot { width:7px; height:7px; border-radius:50%; flex-shrink:0; }
.mp-g  { background:var(--gemini);  box-shadow:0 0 6px var(--gemini); }
.mp-l3 { background:var(--llama33); box-shadow:0 0 6px var(--llama33); }
.mp-l4 { background:var(--llama4);  box-shadow:0 0 6px var(--llama4); }
.model-pill b { color:var(--text-1); font-weight:600; }
.model-pill small { font-size:0.6rem; color:var(--text-3); }

/* ── Hero ── BUG 2 FIX (merged duplicate .hero rule, added centering context) ── */
.hero {
  width: 100%;
  padding: 2.6rem 0 1.8rem;
  text-align: center;
}
/* Pierce Streamlit's internal markdown wrapper which resets text-align to left */
.hero [data-testid="stMarkdownContainer"],
.hero .element-container { text-align: center !important; }

.hero-tag {
  display:inline-flex; align-items:center; gap:0.4rem;
  background:rgba(139,92,246,0.1); border:1px solid rgba(139,92,246,0.25);
  border-radius:99px; padding:0.22rem 0.8rem;
  font-size:0.68rem; font-weight:600; color:#C4B5FD;
  text-transform:uppercase; letter-spacing:0.1em; margin-bottom:1rem;
}
.hero h1 {
  font-size:clamp(2.2rem,5vw,3.8rem) !important; font-weight:800 !important;
  letter-spacing:-0.05em !important; line-height:1 !important; margin:0 0 0.75rem !important;
  background:linear-gradient(135deg,#FFFFFF 0%,#C4B5FD 40%,#67E8F9 85%);
  -webkit-background-clip:text !important; -webkit-text-fill-color:transparent !important; background-clip:text !important;
}
/* BUG 2 FIX: added explicit text-align:center — Streamlit's wrapper resets inheritance */
.hero-sub { font-size:0.92rem; color:var(--text-2); max-width:460px; margin:0 auto; line-height:1.6; text-align:center; }
.hero-bar { width:46px; height:2px; background:linear-gradient(90deg,var(--accent),var(--llama4)); margin:1.3rem auto 0; border-radius:99px; }

/* ── GREEN prompt textarea ── */
.stTextArea textarea {
  background: rgba(74,222,128,0.04) !important;
  border: 1px solid rgba(74,222,128,0.22) !important;
  border-radius: var(--r-md) !important;
  color: var(--green-prompt) !important;
  font-family: var(--mono) !important;
  font-size: 0.87rem !important;
  line-height: 1.75 !important;
  caret-color: var(--green-prompt) !important;
}
.stTextArea textarea::placeholder { color:rgba(74,222,128,0.22) !important; }
.stTextArea textarea:focus {
  border-color:rgba(74,222,128,0.42) !important;
  box-shadow:0 0 0 3px rgba(74,222,128,0.07), 0 0 22px rgba(74,222,128,0.05) !important;
}

/* system prompt — neutral */
.sys-wrap .stTextArea textarea {
  background:var(--bg-raised) !important; border:1px solid var(--border) !important;
  color:var(--text-2) !important; font-family:var(--font) !important; font-size:0.83rem !important;
}
.sys-wrap .stTextArea textarea:focus { border-color:rgba(139,92,246,0.38) !important; box-shadow:0 0 0 2px rgba(139,92,246,0.08) !important; }

/* key inputs */
.stTextInput input {
  background:var(--bg-raised) !important; border:1px solid var(--border) !important;
  border-radius:var(--r-sm) !important; color:var(--text-1) !important;
  font-family:var(--mono) !important; font-size:0.79rem !important;
}
.stTextInput input:focus { border-color:rgba(139,92,246,0.38) !important; box-shadow:0 0 0 2px rgba(139,92,246,0.09) !important; }

/* ── Compare button ── */
.stButton > button {
  background: linear-gradient(135deg,#7C3AED,#8B5CF6,#6D28D9) !important;
  color:#fff !important; border:none !important; border-radius:var(--r-md) !important;
  font-family:var(--font) !important; font-weight:700 !important;
  font-size:0.88rem !important; letter-spacing:0.03em !important;
  padding:0.6rem 2rem !important;
  box-shadow:0 4px 20px rgba(139,92,246,0.32), inset 0 1px 0 rgba(255,255,255,0.12) !important;
  transition:all 0.18s ease !important;
}
.stButton > button:hover { transform:translateY(-2px) !important; box-shadow:0 8px 28px rgba(139,92,246,0.48) !important; }
.stButton > button:active { transform:translateY(0) !important; }

/* template buttons */
div[data-testid="column"] .stButton > button {
  background:var(--bg-raised) !important; border:1px solid var(--border) !important;
  color:var(--text-2) !important; font-size:0.72rem !important; font-weight:500 !important;
  padding:0.28rem 0.65rem !important; box-shadow:none !important; border-radius:7px !important;
}
div[data-testid="column"] .stButton > button:hover {
  border-color:rgba(139,92,246,0.32) !important; color:#C4B5FD !important;
  background:rgba(139,92,246,0.06) !important; transform:none !important; box-shadow:none !important;
}

/* ── Model header badges ── */
.m-badge {
  display:flex; align-items:center; gap:0.5rem; padding:0.65rem 0.95rem;
  border-radius:var(--r-md) var(--r-md) 0 0;
  font-size:0.7rem; font-weight:700; letter-spacing:0.06em; text-transform:uppercase;
  border-bottom:1px solid rgba(255,255,255,0.05);
}
.m-badge .bd { font-size:0.58rem; font-weight:400; opacity:0.5; letter-spacing:0.04em; }
.b-dot { width:8px; height:8px; border-radius:50%; flex-shrink:0; animation:blink 2.6s ease-in-out infinite; }
@keyframes blink { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.45;transform:scale(.78)} }

.bg-gem  { background:rgba(66,133,244,0.09);  color:#93BBFD; border:1px solid rgba(66,133,244,0.2);  border-bottom:none; }
.bg-gem  .b-dot { background:#4285F4; box-shadow:0 0 8px #4285F4; }
.bg-l33  { background:rgba(249,115,22,0.09);  color:#FDBA74; border:1px solid rgba(249,115,22,0.2);  border-bottom:none; }
.bg-l33  .b-dot { background:#F97316; box-shadow:0 0 8px #F97316; }
.bg-l4   { background:rgba(34,211,238,0.09);  color:#67E8F9; border:1px solid rgba(34,211,238,0.2);  border-bottom:none; }
.bg-l4   .b-dot { background:#22D3EE; box-shadow:0 0 8px #22D3EE; }

/* ── Response cards ── */
.r-card {
  background:var(--bg-card); border:1px solid var(--border); border-top:none;
  border-radius:0 0 var(--r-md) var(--r-md); padding:1rem 1rem 0.6rem; min-height:200px;
  transition:border-color .2s;
}
.r-card:hover { border-color:var(--border-h); }
.r-txt { font-size:0.845rem; line-height:1.75; color:var(--text-1); white-space:pre-wrap; word-break:break-word; }
.r-ph {
  display:flex; flex-direction:column; align-items:center; justify-content:center;
  min-height:180px; gap:0.45rem; text-align:center; color:var(--text-3); font-size:0.77rem;
}
.r-ph .pi { font-size:1.5rem; opacity:.28; }
.r-err {
  background:rgba(239,68,68,0.07); border:1px solid rgba(239,68,68,0.17);
  border-radius:7px; padding:0.7rem 0.85rem; color:#FCA5A5;
  font-size:0.77rem; font-family:var(--mono); line-height:1.5;
}
.stats {
  display:flex; gap:0.35rem; flex-wrap:wrap;
  padding:0.6rem 0 0.1rem; border-top:1px solid var(--border); margin-top:0.8rem;
}
.sc {
  background:rgba(255,255,255,0.03); border:1px solid var(--border);
  border-radius:99px; padding:0.16rem 0.5rem;
  font-size:0.64rem; color:var(--text-2); font-family:var(--mono); white-space:nowrap;
}
.sc b { color:var(--text-1); font-weight:500; }

/* ── Metrics ── */
.met-label {
  font-size:0.6rem; font-weight:600; text-transform:uppercase; letter-spacing:0.14em;
  color:var(--text-3); text-align:center; padding:1.5rem 0 0.55rem;
}
[data-testid="stMetric"] {
  background:var(--bg-card) !important; border:1px solid var(--border) !important;
  border-radius:var(--r-md) !important; padding:0.95rem 1.1rem !important; transition:border-color .2s;
}
[data-testid="stMetric"]:hover { border-color:var(--border-h) !important; }
[data-testid="stMetricLabel"] { color:var(--text-3) !important; font-size:0.64rem !important; text-transform:uppercase; letter-spacing:.09em; }
[data-testid="stMetricValue"] { color:var(--text-1) !important; font-family:var(--mono) !important; }
[data-testid="stMetricDelta"]  { font-size:0.66rem !important; }

/* sliders */
.stSlider [data-baseweb="slider"] > div:first-child { background:var(--border) !important; }
.stSlider [data-baseweb="slider"] [role="slider"]   { background:var(--accent) !important; border-color:var(--accent) !important; box-shadow:0 0 0 4px rgba(139,92,246,0.18) !important; }

/* expanders */
.streamlit-expanderHeader { background:var(--bg-raised) !important; border:1px solid var(--border) !important; border-radius:var(--r-sm) !important; color:var(--text-2) !important; font-size:0.78rem !important; font-weight:500 !important; }
.streamlit-expanderContent { background:var(--bg-card) !important; border:1px solid var(--border) !important; border-top:none !important; border-radius:0 0 var(--r-sm) var(--r-sm) !important; }

/* history */
.h-item { background:rgba(255,255,255,0.02); border:1px solid var(--border); border-radius:var(--r-sm); padding:0.65rem 0.85rem; margin-bottom:0.38rem; }
.h-p { font-size:0.78rem; color:var(--green-prompt); font-family:var(--mono); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; margin-bottom:.22rem; }
.h-m { font-size:0.65rem; color:var(--text-3); font-family:var(--mono); }

/* status row */
.st-row { display:flex; align-items:center; gap:0.65rem; flex-wrap:wrap; padding:0.35rem 0; }
.st-pill { display:flex; align-items:center; gap:0.32rem; font-size:0.7rem; color:var(--text-3); }
.sp-d { width:6px; height:6px; border-radius:50%; }
.sp-on  { background:#4ADE80; box-shadow:0 0 5px #4ADE80; }
.sp-off { background:var(--text-3); }
.sp-sep { width:1px; height:13px; background:var(--border); }

/* misc */
label, .stSlider label { color:var(--text-2) !important; font-size:0.74rem !important; font-weight:500 !important; }
hr { border-color:var(--border) !important; margin:0.7rem 0 !important; }
::-webkit-scrollbar { width:4px; height:4px; }
::-webkit-scrollbar-track { background:transparent; }
::-webkit-scrollbar-thumb { background:var(--border); border-radius:99px; }
.stSpinner > div { border-top-color:var(--accent) !important; }
</style>
""", unsafe_allow_html=True)

# ─── API Functions ─────────────────────────────────────────────────────────────

def call_gemini(prompt, system_prompt, api_key, temperature, max_tokens):
    from google import genai
    from google.genai import types
    t0 = time.time()
    try:
        client = genai.Client(api_key=api_key)
        full = f"{system_prompt.strip()}\n\n{prompt}" if system_prompt.strip() else prompt
        resp = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=full,
            config=types.GenerateContentConfig(temperature=temperature, max_output_tokens=max_tokens),
        )
        return {"text": resp.text, "tokens_in": resp.usage_metadata.prompt_token_count,
                "tokens_out": resp.usage_metadata.candidates_token_count, "time": time.time()-t0, "error": None}
    except Exception as e:
        return {"text": None, "tokens_in": 0, "tokens_out": 0, "time": time.time()-t0, "error": str(e)}


def call_groq(model_id, prompt, system_prompt, api_key, temperature, max_tokens):
    from groq import Groq
    t0 = time.time()
    try:
        client = Groq(api_key=api_key)
        msgs = []
        if system_prompt.strip():
            msgs.append({"role": "system", "content": system_prompt.strip()})
        msgs.append({"role": "user", "content": prompt})
        resp = client.chat.completions.create(model=model_id, max_tokens=max_tokens, temperature=temperature, messages=msgs)
        return {"text": resp.choices[0].message.content, "tokens_in": resp.usage.prompt_tokens,
                "tokens_out": resp.usage.completion_tokens, "time": time.time()-t0, "error": None}
    except Exception as e:
        return {"text": None, "tokens_in": 0, "tokens_out": 0, "time": time.time()-t0, "error": str(e)}


def run_all(prompt, sys_p, gkey, gqkey, temp, maxt):
    res = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        futs = {}
        if gkey:  futs["gemini"]  = ex.submit(call_gemini, prompt, sys_p, gkey, temp, maxt)
        if gqkey: futs["llama33"] = ex.submit(call_groq, "llama-3.3-70b-versatile", prompt, sys_p, gqkey, temp, maxt)
        if gqkey: futs["llama4"]  = ex.submit(call_groq, "meta-llama/llama-4-scout-17b-16e-instruct", prompt, sys_p, gqkey, temp, maxt)
        for k, f in futs.items():
            res[k] = f.result()
    return res

# ─── Session State ─────────────────────────────────────────────────────────────
if "history"     not in st.session_state: st.session_state.history     = []
if "prompt_text" not in st.session_state: st.session_state.prompt_text = ""
if "gemini_key"  not in st.session_state: st.session_state.gemini_key  = ""
if "groq_key"    not in st.session_state: st.session_state.groq_key    = ""

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sb-brand">
      <div class="logo-row">
        <div class="logo-box">🔍</div>
        <h2>TripleLensLearning</h2>
      </div>
      <p>Multi-Model AI Comparator</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sb-section">API Keys</div>', unsafe_allow_html=True)
    gemini_key = st.text_input("Gemini API Key", key="gemini_key", type="password", placeholder="AIza...",  help="Google AI Studio — free tier")
    groq_key   = st.text_input("Groq API Key",   key="groq_key",   type="password", placeholder="gsk_...",  help="Covers Llama 3.3 & Llama 4 — free tier")

    st.markdown("---")
    st.markdown('<div class="sb-section">Generation</div>', unsafe_allow_html=True)
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.05)
    max_tokens  = st.slider("Max Tokens",  100, 4000, 1024, 50)

    st.markdown("---")
    st.markdown('<div class="sb-section">Active Models</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="model-list">
      <div class="model-pill"><span class="mp-dot mp-g"></span><span><b>Gemini 2.0 Flash</b><br><small>Google · {'✓ ready' if gemini_key else 'key needed'}</small></span></div>
      <div class="model-pill"><span class="mp-dot mp-l3"></span><span><b>Llama 3.3 · 70B</b><br><small>Meta / Groq · {'✓ ready' if groq_key else 'key needed'}</small></span></div>
      <div class="model-pill"><span class="mp-dot mp-l4"></span><span><b>Llama 4 Scout · 17B</b><br><small>Meta / Groq · {'✓ ready' if groq_key else 'key needed'}</small></span></div>
    </div>
    """, unsafe_allow_html=True)

# ─── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-tag">✦ Parallel AI Inference</div>
  <h1>🔍 TripleLensLearning</h1>
  <p class="hero-sub">One prompt. Three minds. Side-by-side comparison of Gemini, Llama 3.3, and Llama 4 Scout — all in real time.</p>
  <div class="hero-bar"></div>
</div>
""", unsafe_allow_html=True)

# ─── Prompt Templates ──────────────────────────────────────────────────────────
TEMPLATES = {
    "⚡ Code":      "Explain recursion with a clear Python example. Walk through the call stack step by step.",
    "✍️ Writing":  "Write a compelling opening paragraph for a story set in a city that exists only at night.",
    "🔍 Analysis": "Analyze the tradeoffs between microservices and monolithic architecture. When should a team choose each?",
    "💡 Ideas":    "Brainstorm 8 SaaS ideas for remote workers who feel isolated. One-liner and unique twist for each.",
    "📚 Research": "Summarize the strongest arguments for and against universal basic income with key evidence.",
}

with st.expander("📋 Prompt Templates", expanded=False):
    tc = st.columns(len(TEMPLATES))
    for i, (label, text) in enumerate(TEMPLATES.items()):
        if tc[i].button(label, key=f"t{i}"):
            st.session_state.prompt_text = text
            st.session_state["main_p"] = text
            st.rerun()

# ─── System Prompt ─────────────────────────────────────────────────────────────
system_prompt = ""
with st.expander("⚙️ System Prompt (optional)", expanded=False):
    st.markdown('<div class="sys-wrap">', unsafe_allow_html=True)
    system_prompt = st.text_area("System Prompt", height=75,
        placeholder="e.g. You are a concise technical expert. Always answer in bullet points.",
        label_visibility="collapsed", key="sys")
    st.markdown('</div>', unsafe_allow_html=True)

# ─── Prompt Input ──────────────────────────────────────────────────────────────
prompt = st.text_area("Prompt", value=st.session_state.prompt_text, height=130,
    placeholder="Type your question here — sent to all three models simultaneously…",
    label_visibility="collapsed", key="main_p")
if prompt != st.session_state.prompt_text:
    st.session_state.prompt_text = prompt

bc, sc = st.columns([1, 5])
with bc:
    compare = st.button("⚡  Compare Models", use_container_width=True)
with sc:
    n = (1 if gemini_key else 0) + (2 if groq_key else 0)
    g  = f'<span class="st-pill"><span class="sp-d {"sp-on" if gemini_key else "sp-off"}"></span>Gemini</span>'
    l3 = f'<span class="st-pill"><span class="sp-d {"sp-on" if groq_key  else "sp-off"}"></span>Llama 3.3</span>'
    l4 = f'<span class="st-pill"><span class="sp-d {"sp-on" if groq_key  else "sp-off"}"></span>Llama 4</span>'
    ct = f'<span style="font-size:.7rem;color:var(--text-2);font-weight:600;">{n} active</span>'
    st.markdown(f'<div class="st-row">{g}<span class="sp-sep"></span>{l3}<span class="sp-sep"></span>{l4}<span class="sp-sep"></span>{ct}</div>', unsafe_allow_html=True)

# ─── Run ───────────────────────────────────────────────────────────────────────
if compare:
    if not prompt.strip():
        st.warning("Please enter a prompt.")
    elif not gemini_key and not groq_key:
        st.error("Add at least one API key in the sidebar.")
    else:
        with st.spinner("Querying models in parallel…"):
            results = run_all(prompt, system_prompt, gemini_key or "", groq_key or "", temperature, max_tokens)
        st.session_state["last_results"] = results
        st.session_state["last_prompt"]  = prompt
        st.session_state.history.insert(0, {"prompt": prompt, "timestamp": datetime.now().strftime("%H:%M · %b %d"), "models": list(results.keys())})
        if len(st.session_state.history) > 20:
            st.session_state.history = st.session_state.history[:20]

# ─── Model Config ──────────────────────────────────────────────────────────────
MODELS = [
    {"key": "gemini",  "label": "Gemini 2.0 Flash", "prov": "Google",        "cls": "bg-gem", "miss": "Add Gemini key to enable"},
    {"key": "llama33", "label": "Llama 3.3 · 70B",  "prov": "Meta via Groq", "cls": "bg-l33", "miss": "Add Groq key to enable"},
    {"key": "llama4",  "label": "Llama 4 Scout·17B","prov": "Meta via Groq", "cls": "bg-l4",  "miss": "Add Groq key to enable"},
]

# ─── Results ───────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3, gap="medium")
COLS = [c1, c2, c3]

if "last_results" in st.session_state:
    res = st.session_state["last_results"]
    for col, m in zip(COLS, MODELS):
        with col:
            st.markdown(f"""
            <div class="m-badge {m['cls']}">
              <span class="b-dot"></span>
              <div><div style="font-weight:700">{m['label']}</div><div class="bd">{m['prov']}</div></div>
            </div>""", unsafe_allow_html=True)
            if m["key"] in res:
                r = res[m["key"]]
                if r["error"]:
                    # BUG 3 FIX: escape error string too — API errors can contain angle brackets
                    safe_err = html.escape(r["error"])
                    st.markdown(f'<div class="r-card"><div class="r-err">⚠ {safe_err}</div><div class="stats"><span class="sc">⏱ <b>{r["time"]:.2f}s</b></span></div></div>', unsafe_allow_html=True)
                else:
                    # BUG 3 FIX: escape model output before injecting into HTML.
                    # Without this, any model response containing </div>, <script>, or HTML
                    # entities will break card layout or inject executable markup.
                    safe_text = html.escape(r["text"])
                    w = len(r["text"].split()) if r["text"] else 0
                    st.markdown(f"""
                    <div class="r-card">
                      <div class="r-txt">{safe_text}</div>
                      <div class="stats">
                        <span class="sc">⏱ <b>{r['time']:.2f}s</b></span>
                        <span class="sc">↑ <b>{r['tokens_in']:,}</b> in</span>
                        <span class="sc">↓ <b>{r['tokens_out']:,}</b> out</span>
                        <span class="sc">📝 <b>{w}</b> words</span>
                      </div>
                    </div>""", unsafe_allow_html=True)
            else:
                ok = gemini_key if m["key"] == "gemini" else groq_key
                icon = "🔒" if not ok else "◈"
                msg  = m["miss"] if not ok else "Submit a prompt to see response"
                st.markdown(f'<div class="r-card"><div class="r-ph"><span class="pi">{icon}</span><span>{msg}</span></div></div>', unsafe_allow_html=True)

    # Metrics
    valid = {k: v for k, v in res.items() if not v.get("error") and v.get("text")}
    if valid:
        st.markdown('<div class="met-label">⬡ Comparison Metrics</div>', unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3, gap="medium")
        for col, m in zip([m1, m2, m3], MODELS):
            with col:
                k = m["key"]
                if k in valid:
                    r = valid[k]; tps = int(r["tokens_out"]/r["time"]) if r["time"] else 0; w = len(r["text"].split())
                    st.metric(m["label"], f"{r['time']:.2f}s", f"{tps} tok/s · {w} words")
                else:
                    st.metric(m["label"], "—", "Not available")

else:
    for col, m in zip(COLS, MODELS):
        with col:
            ok = gemini_key if m["key"] == "gemini" else groq_key
            icon = "🔒" if not ok else "◈"
            msg  = m["miss"] if not ok else "Submit a prompt to see response"
            st.markdown(f"""
            <div class="m-badge {m['cls']}">
              <span class="b-dot"></span>
              <div><div style="font-weight:700">{m['label']}</div><div class="bd">{m['prov']}</div></div>
            </div>
            <div class="r-card"><div class="r-ph"><span class="pi">{icon}</span><span>{msg}</span></div></div>""", unsafe_allow_html=True)

# ─── History ──────────────────────────────────────────────────────────────────
if st.session_state.history:
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander(f"🕘 Session History ({len(st.session_state.history)} queries)", expanded=False):
        for item in st.session_state.history:
            tags = " · ".join(item["models"])
            st.markdown(f'<div class="h-item"><div class="h-p">{item["prompt"][:130]}{"…" if len(item["prompt"])>130 else ""}</div><div class="h-m">{item["timestamp"]} · {tags}</div></div>', unsafe_allow_html=True)
        if st.button("🗑 Clear History", key="clr"):
            st.session_state.history = []
            st.rerun()
