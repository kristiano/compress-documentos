# 🦴 Caveman Compression

> **Semantic compression for LLM contexts.**  
> Upload a PDF or DOCX → strip grammar → keep facts → save up to **58% of tokens**.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)

---

## What is this?

**Caveman Compression** removes predictable grammar while preserving the unpredictable, factual content that defines meaning — making your texts much leaner for LLM processing.

```
BEFORE (70 tokens)
"In order to optimize the database query performance, we should consider
 implementing an index on the frequently accessed columns..."

AFTER (42 tokens · ↓40%)
"Optimize database query performance. Implement index frequently accessed columns."
```

Facts, numbers, names, and technical terms are always preserved.

---

## Features

| Feature | Details |
|---|---|
| 📄 **PDF upload** | Extracts text from native PDFs |
| 📝 **DOCX upload** | Extracts text from Word documents |
| 🔤 **NLP mode** | Free, offline, multilingual via spaCy (15–30% reduction) |
| 🤖 **MLM mode** | Free, offline, RoBERTa-based (20–30% reduction) |
| ⚡ **LLM mode** | Best quality via OpenAI API (40–58% reduction) |
| 📖 **Decompress** | Expand caveman text back to readable English |
| 📊 **Statistics** | Token count, reduction %, embedding similarity (LLM) |
| ⬇️ **Download** | Export the compressed result as `.txt` |

---

## What gets removed vs. kept

| Removed (predictable) | Kept (factual) |
|---|---|
| Articles: *a, an, the* | Numbers, names, dates |
| Auxiliary verbs: *is, are, was* | Technical terms: *O(log n), JWT, API* |
| Connectives: *therefore, however* | Constraints: *max 500 MB, 3 retries* |
| Fillers: *very, quite, essentially* | Specifics: *Stockholm, 99.9% uptime* |

---

## Run locally

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/caveman-compression-app.git
cd caveman-compression-app
```

### 2. Create virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

> **MLM mode** requires additional packages (heavier, ~500 MB model):
> ```bash
> pip install torch transformers
> python -m spacy download en_core_web_sm
> ```

### 4. (Optional) Add your OpenAI key

```bash
# .streamlit/secrets.toml  ← already in .gitignore
echo 'OPENAI_API_KEY = "sk-..."' >> .streamlit/secrets.toml
```

### 5. Run

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501)

---

## Deploy to Streamlit Cloud

1. **Push this repo to GitHub** (public or private)

2. Go to [share.streamlit.io](https://share.streamlit.io) → **Create app**

3. Select your repository and set:
   - **Main file path:** `app.py`

4. *(Optional — for LLM mode)* Go to **⋮ → Settings → Secrets** and add:
   ```toml
   OPENAI_API_KEY = "sk-..."
   ```

5. Click **Deploy** — done! 🎉

> **Note:** The MLM (RoBERTa) mode requires ~500 MB additional storage.  
> It may exceed Streamlit Cloud's free tier limits. Use NLP or LLM mode for cloud deployment.

---

## Project structure

```
├── app.py                  ← Streamlit UI (upload, compress, download)
├── file_extractor.py       ← PDF & DOCX text extraction
├── compressor_nlp.py       ← NLP-based compressor (spaCy, free, offline)
├── compressor_mlm.py       ← MLM-based compressor (RoBERTa, free, offline)
├── compressor_llm.py       ← LLM-based compressor (OpenAI API)
├── prompts/
│   ├── compression.txt     ← System prompt for LLM compression
│   └── decompression.txt   ← System prompt for LLM decompression
├── requirements.txt        ← Python dependencies
├── packages.txt            ← System packages for Streamlit Cloud
├── README.md
└── .streamlit/
    └── config.toml         ← Light theme configuration
```

---

## Compression methods comparison

| Method | Library | Reduction | Cost | Speed | Offline |
|---|---|---|---|---|---|
| **NLP** | spaCy | 15–30% | Free | <100ms | ✅ |
| **MLM** | RoBERTa | 20–30% | Free | 1–5s | ✅ |
| **LLM** | OpenAI API | 40–58% | Paid | ~2s | ❌ |

---

## When to use Caveman Compression

**✅ Ideal for:**
- LLM reasoning / thinking blocks
- Token-constrained API calls
- RAG knowledge bases (store compressed, save vector space)
- Agent internal reasoning chains
- Internal documentation

**❌ Avoid for:**
- User-facing content
- Legal or compliance documents
- Marketing copy
- Emotional communication

---

## Credits

Based on [caveman-compression](https://github.com/wilpel/caveman-compression) by [William Peltomäki](https://github.com/wilpel).  
Inspired by [TOON](https://github.com/toon-format/toon) and the token-optimization movement.

## License

MIT
