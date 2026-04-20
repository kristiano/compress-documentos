"""
LLM-based caveman compression using OpenAI API.
Best compression quality (40-58% reduction), requires API key.
"""

import os
from pathlib import Path

try:
    from openai import OpenAI
    _openai_available = True
except ImportError:
    _openai_available = False

try:
    import spacy as _spacy
    _spacy_available = True
except ImportError:
    _spacy_available = False

try:
    import numpy as np
    _numpy_available = True
except ImportError:
    _numpy_available = False

PROMPTS_DIR = Path(__file__).parent / 'prompts'

_nlp_cache = {}


def is_available():
    return _openai_available


def load_prompt(filename):
    path = PROMPTS_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")
    return path.read_text()


def count_tokens(text):
    return max(1, len(text.strip()) // 4)


def get_nlp_model(lang='en'):
    if not _spacy_available:
        return None
    if lang in _nlp_cache:
        return _nlp_cache[lang]
    try:
        nlp = _spacy.load('en_core_web_sm')
        _nlp_cache[lang] = nlp
        return nlp
    except OSError:
        return None


def is_text_content(text):
    """Detect if content is natural language vs code/structured data."""
    code_indicators = [
        'def ', 'class ', 'function ', 'import ', 'const ', 'let ', 'var ',
        'public ', 'private ', 'protected ', '#include', 'package ',
        '=>', '->', '::', '!=', '==', '<=', '>=', '&&', '||',
    ]
    code_score = sum(1 for ind in code_indicators if ind in text)
    brace_count = text.count('{') + text.count('}') + text.count('[') + text.count(']')
    words = text.split()
    if len(words) < 5:
        return True
    if code_score >= 2 or brace_count > len(words) * 0.2:
        return False
    return True


def split_sentences(text):
    nlp = get_nlp_model()
    if nlp is None:
        # Fallback: naive split
        import re
        return [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
    doc = nlp(text)
    return [sent.text for sent in doc.sents]


def cosine_similarity(v1, v2):
    if not _numpy_available:
        return None
    v1, v2 = np.array(v1), np.array(v2)
    denom = np.linalg.norm(v1) * np.linalg.norm(v2)
    if denom == 0:
        return 0.0
    return float(np.dot(v1, v2) / denom)


def get_embedding(client, text, model="text-embedding-3-large"):
    try:
        resp = client.embeddings.create(input=text, model=model)
        return resp.data[0].embedding
    except Exception:
        return None


def calc_embedding_similarity(client, original, compressed):
    if not _numpy_available:
        return None, None
    e1 = get_embedding(client, original)
    e2 = get_embedding(client, compressed)
    if e1 is None or e2 is None:
        return None, None
    sim = cosine_similarity(e1, e2)
    return sim, 1.0 - sim  # similarity, loss


def compress_text(text, api_key, model="gpt-4o-mini", calc_embeddings=False):
    """
    Compress text using OpenAI LLM.
    Returns: (compressed_text, orig_tokens, comp_tokens, reduction_pct, similarity, loss, error)
    """
    if not _openai_available:
        return None, 0, 0, 0, None, None, "openai package not installed. Run: pip install openai"

    try:
        compression_prompt = load_prompt('compression.txt')
    except FileNotFoundError as e:
        return None, 0, 0, 0, None, None, str(e)

    try:
        client = OpenAI(api_key=api_key)

        prompt = compression_prompt.format(text=text)
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert at caveman compression. Always compress the provided text, never ask for clarification. Return ONLY the compressed text."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )
        compressed = resp.choices[0].message.content.strip()

        orig_tokens = count_tokens(text)
        comp_tokens = count_tokens(compressed)
        reduction = ((orig_tokens - comp_tokens) / orig_tokens * 100) if orig_tokens > 0 else 0.0

        similarity, loss = None, None
        if calc_embeddings:
            similarity, loss = calc_embedding_similarity(client, text, compressed)

        return compressed, orig_tokens, comp_tokens, reduction, similarity, loss, None

    except Exception as e:
        return None, 0, 0, 0, None, None, str(e)


def decompress_text(text, api_key, model="gpt-4o-mini"):
    """
    Decompress caveman text using OpenAI LLM.
    Returns: (decompressed_text, cave_tokens, norm_tokens, expansion_pct, error)
    """
    if not _openai_available:
        return None, 0, 0, 0, "openai package not installed. Run: pip install openai"

    try:
        decompression_prompt = load_prompt('decompression.txt')
    except FileNotFoundError as e:
        return None, 0, 0, 0, str(e)

    try:
        client = OpenAI(api_key=api_key)
        prompt = decompression_prompt.format(text=text)
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert at expanding compressed text."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )
        decompressed = resp.choices[0].message.content.strip()

        cave_tokens = count_tokens(text)
        norm_tokens = count_tokens(decompressed)
        expansion = ((norm_tokens - cave_tokens) / cave_tokens * 100) if cave_tokens > 0 else 0.0

        return decompressed, cave_tokens, norm_tokens, expansion, None

    except Exception as e:
        return None, 0, 0, 0, str(e)
