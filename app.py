"""
Caveman Compression — Streamlit Interface
Upload PDF or DOCX → semantic compression for LLM contexts.
"""

import streamlit as st

# ── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Caveman Compression",
    page_icon="🦴",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.stApp { background: #f8f9fb !important; }

section[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #e5e7eb !important;
}
section[data-testid="stSidebar"] * { color: #374151 !important; }

/* Hero */
.hero { text-align: center; padding: 2rem 1rem 1.2rem; }
.hero-eyebrow {
    font-size: 0.76rem; font-weight: 700; letter-spacing: 0.12em;
    text-transform: uppercase; color: #f97316; margin-bottom: 0.5rem;
}
.hero-title {
    font-size: 2.6rem; font-weight: 800; color: #111827;
    letter-spacing: -1.5px; line-height: 1.1; margin-bottom: 0.5rem;
}
.hero-title span {
    background: linear-gradient(90deg, #f97316, #ea580c);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.hero-sub { font-size: 0.97rem; color: #6b7280; max-width: 560px; margin: 0 auto; line-height: 1.65; }

/* Section label */
.slabel {
    font-size: 0.71rem; font-weight: 700; letter-spacing: 0.1em;
    text-transform: uppercase; color: #9ca3af; margin-bottom: 0.45rem;
}

/* Divider */
.hr { height: 1px; background: #f3f4f6; margin: 1rem 0; }

/* Upload dropzone override */
div[data-testid="stFileUploader"] {
    border: 2px dashed #d1d5db !important;
    border-radius: 14px !important;
    background: #ffffff !important;
    padding: 0.5rem !important;
    transition: border-color 0.2s;
}
div[data-testid="stFileUploader"]:hover { border-color: #f97316 !important; }
div[data-testid="stFileUploader"] label { color: #374151 !important; }

/* Extracted text preview */
.preview-box {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem; color: #374151;
    background: #f9fafb; border: 1px solid #e5e7eb;
    border-radius: 10px; padding: 1rem 1.2rem;
    line-height: 1.7; white-space: pre-wrap; word-break: break-word;
    max-height: 220px; overflow-y: auto;
}
/* Output text */
.output-text {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.88rem; color: #1f2937;
    background: #f9fafb; border: 1px solid #e5e7eb;
    border-radius: 10px; padding: 1.1rem 1.3rem;
    line-height: 1.75; white-space: pre-wrap; word-break: break-word;
    min-height: 160px;
}

/* File info card */
.file-card {
    display: flex; align-items: center; gap: 0.75rem;
    background: #ffffff; border: 1px solid #e5e7eb;
    border-radius: 10px; padding: 0.75rem 1rem;
    margin-bottom: 0.75rem;
}
.file-icon { font-size: 1.6rem; line-height: 1; }
.file-name { font-weight: 600; font-size: 0.9rem; color: #111827; }
.file-meta { font-size: 0.78rem; color: #6b7280; }

/* Stat pills */
.stats-row { display: flex; gap: 0.6rem; flex-wrap: wrap; margin-top: 0.9rem; align-items: center; }
.pill { display: inline-flex; align-items: center; padding: 0.3rem 0.85rem; border-radius: 999px; font-size: 0.8rem; font-weight: 600; white-space: nowrap; }
.pill-gray   { background: #f3f4f6; color: #4b5563; border: 1px solid #d1d5db; }
.pill-green  { background: #f0fdf4; color: #15803d; border: 1px solid #bbf7d0; }
.pill-blue   { background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; }
.pill-purple { background: #faf5ff; color: #7e22ce; border: 1px solid #e9d5ff; }
.pill-orange { background: #fff7ed; color: #c2410c; border: 1px solid #fed7aa; }

/* Badges */
.badge { display: inline-flex; align-items: center; padding: 0.25rem 0.75rem; border-radius: 999px; font-size: 0.72rem; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; }
.badge-nlp  { background: #f0fdf4; color: #16a34a; border: 1px solid #86efac; }
.badge-mlm  { background: #faf5ff; color: #9333ea; border: 1px solid #d8b4fe; }
.badge-llm  { background: #fff7ed; color: #ea580c; border: 1px solid #fdba74; }

/* quality */
.quality { display: inline-flex; align-items: center; gap: 0.4rem; padding: 0.4rem 1rem; border-radius: 999px; font-size: 0.82rem; font-weight: 600; margin-top: 0.7rem; }
.q-excellent { background: #f0fdf4; color: #15803d; border: 1px solid #86efac; }
.q-good      { background: #eff6ff; color: #1d4ed8; border: 1px solid #93c5fd; }
.q-moderate  { background: #fffbeb; color: #b45309; border: 1px solid #fcd34d; }
.q-poor      { background: #fef2f2; color: #dc2626; border: 1px solid #fca5a5; }

/* Info card sidebar */
.info-card { border-radius: 10px; padding: 0.8rem 1rem; font-size: 0.83rem; line-height: 1.6; margin-bottom: 0.75rem; }
.info-green  { background: #f0fdf4; border: 1px solid #86efac; color: #166534; }
.info-purple { background: #faf5ff; border: 1px solid #d8b4fe; color: #6b21a8; }
.info-orange { background: #fff7ed; border: 1px solid #fdba74; color: #9a3412; }

/* Button overrides */
div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #f97316, #ea580c) !important;
    color: #fff !important; border: none !important;
    border-radius: 10px !important; font-weight: 700 !important;
    font-size: 0.95rem !important; padding: 0.6rem 1.6rem !important;
    font-family: 'Inter', sans-serif !important;
    box-shadow: 0 2px 8px rgba(249,115,22,0.28) !important;
    transition: all 0.2s ease !important;
}
div[data-testid="stButton"] > button:hover {
    opacity: 0.9 !important; transform: translateY(-1px) !important;
}
div[data-testid="stTextInput"] input {
    background: #fff !important; border: 1.5px solid #d1d5db !important;
    border-radius: 8px !important; color: #111827 !important;
}
label, .stSelectbox label, .stRadio label { color: #374151 !important; font-size: 0.85rem !important; font-weight: 500 !important; }
h1,h2,h3 { color: #111827 !important; }
div[data-testid="stSelectbox"] > div > div { background: #fff !important; border: 1.5px solid #d1d5db !important; border-radius: 8px !important; color: #111827 !important; }

/* Download button */
div[data-testid="stDownloadButton"] > button {
    background: #ffffff !important;
    color: #374151 !important;
    border: 1.5px solid #d1d5db !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    box-shadow: none !important;
}
div[data-testid="stDownloadButton"] > button:hover {
    border-color: #f97316 !important;
    color: #f97316 !important;
    transform: none !important;
}
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-eyebrow">🦴 Semantic Token Compression</div>
  <div class="hero-title">Caveman <span>Compression</span></div>
  <div class="hero-sub">
      Upload a PDF or DOCX · Strip grammar · Keep facts · Save tokens.<br>
      Compress LLM contexts by up to <b>58%</b> while preserving all semantic meaning.
  </div>
</div>
<div class="hr"></div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    mode = st.radio("Operation", ["🗜️ Compress", "📖 Decompress"], index=0)

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)
    st.markdown("**Method**")

    method = st.selectbox(
        "Method",
        ["NLP — Free & Offline", "MLM — RoBERTa (Free, Offline)", "LLM — OpenAI API (Best Quality)"],
        index=0,
        label_visibility="collapsed",
    )

    if "NLP" in method:
        st.markdown("""<div class="info-card info-green">
        ✅ <b>NLP (spaCy)</b><br>Free · No GPU · Multilingual<br>
        Reduction: 15–30% · Speed: &lt;100ms
        </div>""", unsafe_allow_html=True)
    elif "MLM" in method:
        st.markdown("""<div class="info-card info-purple">
        🤖 <b>MLM (RoBERTa)</b><br>Free · Local model (~500 MB)<br>
        Reduction: 20–30% · Speed: 1–5s/doc
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div class="info-card info-orange">
        ⚡ <b>LLM (OpenAI)</b><br>Best quality · API key required<br>
        Reduction: 40–58% · Speed: ~2s/req
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    # Language (NLP only)
    lang = 'en'
    if "NLP" in method and "Compress" in mode:
        st.markdown("**Language**")
        lang_map = {
            "English (en)": "en", "Spanish (es)": "es", "German (de)": "de",
            "French (fr)": "fr", "Italian (it)": "it", "Portuguese (pt)": "pt",
            "Dutch (nl)": "nl", "Russian (ru)": "ru", "Chinese (zh)": "zh",
            "Japanese (ja)": "ja", "Polish (pl)": "pl",
        }
        lang = lang_map[st.selectbox("Language", list(lang_map.keys()), index=0, label_visibility="collapsed")]
        st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    # MLM options
    mlm_threshold, mlm_no_adjacent, mlm_protect_ner = 1e-5, False, True
    if "MLM" in method and "Compress" in mode:
        st.markdown("**Compression Level**")
        lbl = st.select_slider(
            "Level",
            ["Conservative (1e-3)", "Moderate (1e-4)", "Balanced (1e-5)", "Aggressive (1e-6)"],
            value="Balanced (1e-5)", label_visibility="collapsed",
        )
        mlm_threshold = {"Conservative (1e-3)": 1e-3, "Moderate (1e-4)": 1e-4,
                         "Balanced (1e-5)": 1e-5, "Aggressive (1e-6)": 1e-6}[lbl]
        mlm_no_adjacent = st.checkbox("No adjacent removal", value=False)
        mlm_protect_ner = st.checkbox("Protect named entities", value=True)
        st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    # OpenAI
    openai_key, openai_model, calc_embeddings = "", "gpt-4o-mini", False
    if "LLM" in method:
        st.markdown("**OpenAI API Key**")
        default_key = ""
        try:
            default_key = st.secrets.get("OPENAI_API_KEY", "")
        except Exception:
            pass
        openai_key = st.text_input("Key", value=default_key, type="password",
                                   placeholder="sk-...", label_visibility="collapsed")
        if not default_key:
            st.caption("💡 On Streamlit Cloud add your key in **App Settings → Secrets**.")
        st.markdown("**Model**")
        openai_model = st.selectbox("Model", ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
                                    index=0, label_visibility="collapsed")
        if "Compress" in mode:
            calc_embeddings = st.checkbox("Embedding similarity", value=False,
                                          help="Compute cosine similarity (costs extra API calls).")
        st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="font-size:0.75rem;color:#9ca3af;text-align:center;line-height:1.7;">
        Based on <a href="https://github.com/wilpel/caveman-compression"
        style="color:#f97316;text-decoration:none;" target="_blank">caveman-compression</a><br>
        by William Peltomäki · MIT License
    </div>""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────
def quality_badge(sim):
    if sim is None:
        return ""
    if sim >= 0.95:
        return f'<div class="quality q-excellent">✅ Excellent — {sim:.4f}</div>'
    if sim >= 0.90:
        return f'<div class="quality q-good">🔵 Good — {sim:.4f}</div>'
    if sim >= 0.85:
        return f'<div class="quality q-moderate">⚠️ Moderate — {sim:.4f}</div>'
    return f'<div class="quality q-poor">❌ Poor — {sim:.4f}</div>'


def file_icon(name: str) -> str:
    return "📄" if name.lower().endswith(".pdf") else "📝"


def human_size(n: int) -> str:
    if n < 1024:
        return f"{n} B"
    if n < 1024 ** 2:
        return f"{n/1024:.1f} KB"
    return f"{n/1024**2:.1f} MB"


# ── Two-column layout ─────────────────────────────────────────────────────
col_in, col_out = st.columns(2, gap="large")

# ────────────────────── LEFT: upload ──────────────────────────────────────
with col_in:
    st.markdown('<div class="slabel">Upload File</div>', unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Upload",
        type=["pdf", "docx"],
        accept_multiple_files=False,
        label_visibility="collapsed",
        help="Supported formats: PDF, DOCX",
    )

    extracted_text = ""

    if uploaded is not None:
        file_bytes = uploaded.read()
        icon = file_icon(uploaded.name)
        size_str = human_size(len(file_bytes))

        st.markdown(f"""
        <div class="file-card">
          <div class="file-icon">{icon}</div>
          <div>
            <div class="file-name">{uploaded.name}</div>
            <div class="file-meta">{size_str}</div>
          </div>
        </div>""", unsafe_allow_html=True)

        # Extract text
        from file_extractor import extract_text
        with st.spinner("Extracting text…"):
            extracted_text, extract_err = extract_text(file_bytes, uploaded.name)

        if extract_err:
            st.error(f"❌ {extract_err}")
        else:
            word_count = len(extracted_text.split())
            token_est = max(1, len(extracted_text) // 4)
            st.markdown(f"""
            <div class="stats-row">
                <span class="pill pill-gray">~{word_count:,} words</span>
                <span class="pill pill-blue">≈ {token_est:,} tokens</span>
            </div>""", unsafe_allow_html=True)

            st.markdown('<div class="hr" style="margin-top:0.8rem;"></div>', unsafe_allow_html=True)
            st.markdown('<div class="slabel">Extracted Text Preview</div>', unsafe_allow_html=True)
            preview = extracted_text[:1200] + ("…" if len(extracted_text) > 1200 else "")
            st.markdown(f'<div class="preview-box">{preview}</div>', unsafe_allow_html=True)

    # Action button
    st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)
    run_label = "🗜️  Compress File" if "Compress" in mode else "📖  Decompress File"
    run_clicked = st.button(run_label, use_container_width=True, key="run_btn",
                            disabled=(not extracted_text))

# ────────────────────── RIGHT: output ─────────────────────────────────────
with col_out:
    st.markdown('<div class="slabel">Result</div>', unsafe_allow_html=True)
    out_ph = st.empty()
    stats_ph = st.empty()
    dl_ph = st.empty()

    out_ph.markdown(
        '<div class="output-text" style="color:#9ca3af;font-style:italic;">'
        'Upload a file and click Compress to see the result here…'
        '</div>',
        unsafe_allow_html=True,
    )

# ── Processing ────────────────────────────────────────────────────────────
if run_clicked and extracted_text:

    input_text = extracted_text

    # ── NLP ──────────────────────────────────────────────────────────────
    if "NLP" in method:
        if "Compress" in mode:
            from compressor_nlp import compress_text, count_tokens
            with st.spinner("Compressing with spaCy…"):
                result, err = compress_text(input_text, lang=lang)
            if err:
                st.error(f"❌ {err}")
                st.stop()
            orig_t = count_tokens(input_text)
            comp_t = count_tokens(result)
            red = ((orig_t - comp_t) / orig_t * 100) if orig_t > 0 else 0
            out_ph.markdown(f'<div class="output-text">{result}</div>', unsafe_allow_html=True)
            stats_ph.markdown(f"""
            <div class="stats-row">
                <span class="pill pill-gray">{orig_t:,} → {comp_t:,} tokens</span>
                <span class="pill pill-green">↓ {red:.1f}% reduction</span>
                <span class="badge badge-nlp">NLP</span>
            </div>""", unsafe_allow_html=True)
            dl_ph.download_button("⬇️ Download compressed .txt", data=result,
                                  file_name="compressed.txt", mime="text/plain")
        else:
            from compressor_nlp import decompress_text
            result = decompress_text(input_text)
            out_ph.markdown(f'<div class="output-text">{result}</div>', unsafe_allow_html=True)
            stats_ph.markdown('<span class="badge badge-nlp">NLP · Decompress</span>', unsafe_allow_html=True)
            dl_ph.download_button("⬇️ Download .txt", data=result,
                                  file_name="decompressed.txt", mime="text/plain")

    # ── MLM ──────────────────────────────────────────────────────────────
    elif "MLM" in method:
        from compressor_mlm import is_available, get_missing_packages, count_tokens
        if not is_available():
            missing = get_missing_packages()
            st.error(f"❌ Missing: `{', '.join(missing)}`\n\nRun: `pip install {' '.join(missing)}`")
            st.stop()
        if "Compress" in mode:
            from compressor_mlm import compress_text
            pb = st.progress(0, text="Loading RoBERTa…")

            def _cb(cur, tot):
                pb.progress(min(cur / max(tot, 1), 1.0), text=f"Word {cur}/{tot}…")

            result, err = compress_text(
                input_text,
                prob_threshold=mlm_threshold,
                no_adjacent_removal=mlm_no_adjacent,
                protect_ner=mlm_protect_ner,
                progress_callback=_cb,
            )
            pb.empty()
            if err:
                st.error(f"❌ {err}")
                st.stop()
            orig_t = count_tokens(input_text)
            comp_t = count_tokens(result)
            red = ((orig_t - comp_t) / orig_t * 100) if orig_t > 0 else 0
            out_ph.markdown(f'<div class="output-text">{result}</div>', unsafe_allow_html=True)
            stats_ph.markdown(f"""
            <div class="stats-row">
                <span class="pill pill-gray">{orig_t:,} → {comp_t:,} tokens</span>
                <span class="pill pill-green">↓ {red:.1f}% reduction</span>
                <span class="pill pill-purple">P ≥ {mlm_threshold:.0e}</span>
                <span class="badge badge-mlm">RoBERTa</span>
            </div>""", unsafe_allow_html=True)
            dl_ph.download_button("⬇️ Download compressed .txt", data=result,
                                  file_name="compressed.txt", mime="text/plain")
        else:
            from compressor_mlm import decompress_text
            result = decompress_text(input_text)
            out_ph.markdown(f'<div class="output-text">{result}</div>', unsafe_allow_html=True)
            stats_ph.markdown('<span class="badge badge-mlm">RoBERTa · Decompress</span>', unsafe_allow_html=True)
            dl_ph.download_button("⬇️ Download .txt", data=result,
                                  file_name="decompressed.txt", mime="text/plain")

    # ── LLM ──────────────────────────────────────────────────────────────
    else:
        if not openai_key.strip():
            st.error("❌ Enter your OpenAI API key in the sidebar.")
            st.stop()
        from compressor_llm import is_available as llm_ok
        if not llm_ok():
            st.error("❌ `openai` not installed.")
            st.stop()

        if "Compress" in mode:
            from compressor_llm import compress_text
            with st.spinner("Compressing with OpenAI…"):
                result, orig_t, comp_t, red, sim, loss, err = compress_text(
                    input_text, api_key=openai_key, model=openai_model,
                    calc_embeddings=calc_embeddings,
                )
            if err:
                st.error(f"❌ {err}")
                st.stop()
            out_ph.markdown(f'<div class="output-text">{result}</div>', unsafe_allow_html=True)
            stats_ph.markdown(f"""
            <div class="stats-row">
                <span class="pill pill-gray">{orig_t:,} → {comp_t:,} tokens</span>
                <span class="pill pill-green">↓ {red:.1f}% reduction</span>
                <span class="badge badge-llm">LLM / {openai_model}</span>
            </div>
            {quality_badge(sim) if calc_embeddings else ""}
            """, unsafe_allow_html=True)
            dl_ph.download_button("⬇️ Download compressed .txt", data=result,
                                  file_name="compressed.txt", mime="text/plain")
        else:
            from compressor_llm import decompress_text
            with st.spinner("Decompressing…"):
                result, cave_t, norm_t, exp, err = decompress_text(
                    input_text, api_key=openai_key, model=openai_model
                )
            if err:
                st.error(f"❌ {err}")
                st.stop()
            out_ph.markdown(f'<div class="output-text">{result}</div>', unsafe_allow_html=True)
            stats_ph.markdown(f"""
            <div class="stats-row">
                <span class="pill pill-gray">{cave_t:,} → {norm_t:,} tokens</span>
                <span class="pill pill-green">↑ {exp:.1f}% expansion</span>
                <span class="badge badge-llm">LLM / {openai_model}</span>
            </div>""", unsafe_allow_html=True)
            dl_ph.download_button("⬇️ Download .txt", data=result,
                                  file_name="decompressed.txt", mime="text/plain")

# ── How it works ──────────────────────────────────────────────────────────
st.markdown('<div class="hr" style="margin-top:2rem;"></div>', unsafe_allow_html=True)
with st.expander("ℹ️ How Caveman Compression works"):
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
**What gets removed** *(predictable)*
- Articles: *a, an, the*
- Auxiliary verbs: *is, are, was, were, have*
- Connectives: *therefore, however, because*
- Filler: *very, quite, essentially*
""")
    with c2:
        st.markdown("""
**What stays** *(unpredictable / factual)*
- **Numbers, names, dates**
- **Technical terms** — *O(log n), API, JWT*
- **Constraints** — *max 500 MB, 3 retries*
- **Specifics** — *Stockholm, 99.9% uptime*
""")
    st.markdown("""
| Method | Reduction | Cost | Offline |
|---|---|---|---|
| NLP (spaCy) | 15–30% | Free | ✅ |
| MLM (RoBERTa) | 20–30% | Free | ✅ |
| LLM (OpenAI) | 40–58% | API key | ❌ |

**✅ Good for:** LLM reasoning · token-constrained contexts · internal docs  
**❌ Avoid for:** user-facing copy · legal docs · emotional communication
""")
