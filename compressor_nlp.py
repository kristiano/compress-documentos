"""
NLP-based caveman compression without LLM.
Fast, free, deterministic - uses stop word removal and grammar stripping.
Supports multiple languages via spaCy.
"""

import sys

try:
    import spacy
except ImportError:
    spacy = None

_nlp_models = {}

SPACY_MODELS = {
    'en': 'en_core_web_sm',
    'es': 'es_core_news_sm',
    'de': 'de_core_news_sm',
    'fr': 'fr_core_news_sm',
    'it': 'it_core_news_sm',
    'pt': 'pt_core_news_sm',
    'nl': 'nl_core_news_sm',
    'el': 'el_core_news_sm',
    'nb': 'nb_core_news_sm',
    'lt': 'lt_core_news_sm',
    'ja': 'ja_core_news_sm',
    'zh': 'zh_core_web_sm',
    'pl': 'pl_core_news_sm',
    'ro': 'ro_core_news_sm',
    'ru': 'ru_core_news_sm',
}


def is_available():
    """Check if spaCy is installed."""
    return spacy is not None


def get_nlp_model(lang='en'):
    """Load or retrieve cached spaCy model. Returns (model, error_message)."""
    if spacy is None:
        return None, "spaCy not installed. Run: pip install spacy"

    if lang in _nlp_models:
        return _nlp_models[lang], None

    model_name = SPACY_MODELS.get(lang, 'xx_ent_wiki_sm')

    try:
        nlp = spacy.load(model_name)
    except OSError:
        try:
            nlp = spacy.load('xx_ent_wiki_sm')
            model_name = 'xx_ent_wiki_sm'
        except OSError:
            return None, (
                f"spaCy model '{model_name}' not found.\n"
                f"Install with: python -m spacy download {model_name}"
            )

    _nlp_models[lang] = nlp
    return nlp, None


def count_tokens(text):
    """Estimate token count: characters / 4."""
    return max(1, len(text.strip()) // 4)


def compress_text(text, lang='en'):
    """Apply NLP-based compression using spaCy. Returns (result, error)."""
    nlp, error = get_nlp_model(lang)
    if error:
        return None, error

    doc = nlp(text)
    compressed_sentences = []

    for sent in doc.sents:
        kept_tokens = []

        for token in sent:
            if token.is_punct and token.text not in ['-', '/', ':', '%', '$', '€', '£']:
                continue
            if token.is_stop:
                continue
            if token.pos_ == 'AUX':
                continue
            if token.pos_ == 'DET':
                continue
            if token.pos_ == 'ADV' and token.text.lower() in {
                'very', 'really', 'quite', 'extremely', 'incredibly', 'absolutely',
                'totally', 'completely', 'utterly', 'highly', 'particularly',
                'especially', 'truly', 'actually', 'basically', 'essentially'
            }:
                continue
            if token.pos_ == 'CCONJ' and token.text.lower() in {'and', 'or'}:
                continue

            kept_tokens.append(token.text)

        if kept_tokens:
            compressed_sentences.append(' '.join(kept_tokens) + '.')

    result = ' '.join(compressed_sentences)
    if result:
        result = result[0].upper() + result[1:]

    return result, None


def decompress_text(text):
    """Simple formatting cleanup — capitalizes sentences."""
    sentences = text.split('.')
    result = []
    for sentence in sentences:
        sentence = sentence.strip()
        if sentence:
            sentence = sentence[0].upper() + sentence[1:]
            result.append(sentence)
    return '. '.join(result) + '.'
