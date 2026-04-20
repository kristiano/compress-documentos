"""
MLM-based caveman compression using RoBERTa.
Removes highly predictable tokens based on masked language model probabilities.
No LLM API required - uses local RoBERTa model.
"""

import sys

_torch_available = False
_transformers_available = False
_spacy_available = False

try:
    import torch
    import torch.nn.functional as F
    _torch_available = True
except ImportError:
    pass

try:
    from transformers import RobertaForMaskedLM, RobertaTokenizer
    _transformers_available = True
except ImportError:
    pass

try:
    import spacy as _spacy
    _spacy_available = True
except ImportError:
    pass

_roberta_model = None
_roberta_tokenizer = None
_device = None
_nlp = None


def is_available():
    return _torch_available and _transformers_available and _spacy_available


def get_missing_packages():
    missing = []
    if not _torch_available:
        missing.append("torch")
    if not _transformers_available:
        missing.append("transformers")
    if not _spacy_available:
        missing.append("spacy")
    return missing


def get_models():
    """Load or retrieve cached models. Returns (roberta_model, tokenizer, device, nlp, error)."""
    global _roberta_model, _roberta_tokenizer, _device, _nlp

    missing = get_missing_packages()
    if missing:
        return None, None, None, None, f"Missing packages: {', '.join(missing)}. Run: pip install {' '.join(missing)}"

    if _roberta_model is None:
        try:
            _device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            _roberta_tokenizer = RobertaTokenizer.from_pretrained('roberta-base')
            _roberta_model = RobertaForMaskedLM.from_pretrained('roberta-base').to(_device)
            _roberta_model.eval()
        except Exception as e:
            return None, None, None, None, f"Failed to load RoBERTa model: {e}"

        try:
            _nlp = _spacy.load('en_core_web_sm')
        except OSError:
            return None, None, None, None, (
                "spaCy model 'en_core_web_sm' not found.\n"
                "Install with: python -m spacy download en_core_web_sm"
            )

    return _roberta_model, _roberta_tokenizer, _device, _nlp, None


def count_tokens(text):
    return max(1, len(text.strip()) // 4)


def get_mlm_probability(model, tokenizer, device, sentence, word_idx):
    """Get MLM probability for a specific word in a sentence."""
    words = sentence.split()
    if word_idx >= len(words):
        return 0.0

    target_word = words[word_idx]
    masked_words = words.copy()
    masked_words[word_idx] = tokenizer.mask_token
    masked_sentence = " ".join(masked_words)

    try:
        inputs = tokenizer(masked_sentence, return_tensors="pt", max_length=512, truncation=True).to(device)
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits

        mask_token_index = (inputs.input_ids == tokenizer.mask_token_id).nonzero(as_tuple=True)[1]
        if len(mask_token_index) == 0:
            return 0.0

        mask_token_logits = logits[0, mask_token_index[0], :]
        probs = F.softmax(mask_token_logits, dim=0)

        target_tokens = tokenizer.encode(target_word, add_special_tokens=False)
        if not target_tokens:
            return 0.0

        return float(probs[target_tokens[0]].item())

    except Exception:
        return 0.0


def compress_text(text, prob_threshold=1e-5, no_adjacent_removal=False, protect_ner=True,
                  progress_callback=None):
    """
    Compress text using MLM (RoBERTa) probabilities.
    Returns: (compressed_text, error)
    progress_callback(current, total) called during processing.
    """
    model, tokenizer, device, nlp, error = get_models()
    if error:
        return None, error

    PROTECTED_NER = {'PERSON', 'ORG', 'GPE', 'DATE', 'MONEY', 'PERCENT',
                     'TIME', 'QUANTITY', 'CARDINAL', 'ORDINAL', 'LOC', 'FAC'}

    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents]
    total_words = sum(len(s.split()) for s in sentences)
    processed = 0

    words_to_remove = set()
    protected_positions = set()

    for sent_idx, sentence in enumerate(sentences):
        sent_doc = nlp(sentence)
        words = [token.text for token in sent_doc if not token.is_punct and not token.is_space]

        if not words:
            continue

        if protect_ner:
            word_tokens = [token for token in sent_doc if not token.is_punct and not token.is_space]
            for ent in sent_doc.ents:
                if ent.label_ in PROTECTED_NER:
                    for word_idx, token in enumerate(word_tokens):
                        if token.idx >= ent.start_char and token.idx < ent.end_char:
                            protected_positions.add((sent_idx, word_idx))
                        elif token.idx + len(token.text) > ent.start_char and token.idx < ent.end_char:
                            protected_positions.add((sent_idx, word_idx))

        word_probs = []
        for word_idx, word in enumerate(words):
            prob = get_mlm_probability(model, tokenizer, device, sentence, word_idx)
            word_probs.append((sent_idx, word_idx, prob))
            processed += 1
            if progress_callback:
                progress_callback(processed, total_words)

        if no_adjacent_removal:
            candidates = [(s, w, p) for s, w, p in word_probs if p >= prob_threshold]
            candidates.sort(key=lambda x: x[2], reverse=True)
            removed_indices = set()
            for sent_i, word_i, prob in candidates:
                if protect_ner and (sent_i, word_i) in protected_positions:
                    continue
                if (sent_i, word_i - 1) not in removed_indices and (sent_i, word_i + 1) not in removed_indices:
                    removed_indices.add((sent_i, word_i))
                    words_to_remove.add((sent_i, word_i))
        else:
            for sent_i, word_i, prob in word_probs:
                if prob >= prob_threshold:
                    if protect_ner and (sent_i, word_i) in protected_positions:
                        continue
                    words_to_remove.add((sent_i, word_i))

    compressed_sentences = []
    for sent_idx, sentence in enumerate(sentences):
        sent_doc = nlp(sentence)
        words = [token.text for token in sent_doc if not token.is_punct and not token.is_space]
        if not words:
            compressed_sentences.append(sentence)
            continue

        remaining = [w for word_idx, w in enumerate(words)
                     if (sent_idx, word_idx) not in words_to_remove]
        if not remaining:
            remaining = words[:min(3, len(words))]

        compressed_sentences.append(' '.join(remaining))

    result = ' '.join(compressed_sentences)
    if result and result[0].islower():
        result = result[0].upper() + result[1:]

    return result, None


def decompress_text(text):
    """Simple formatting cleanup."""
    sentences = text.split('.')
    result = []
    for sentence in sentences:
        sentence = sentence.strip()
        if sentence:
            sentence = sentence[0].upper() + sentence[1:]
            result.append(sentence)
    return '. '.join(result) + '.' if result else ''
