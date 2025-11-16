"""Lightweight query preprocessing utilities.

Default behavior is noop. Two optional modes are provided:
- light: conservative normalization (lowercase, whitespace/punctuation cleanup, remove filler words)
- spell: vocabulary-aware conservative spell correction using difflib (only replaces high-confidence single-word typos)

These functions are designed to be safe (no external deps) and conservative so we avoid changing intent.
"""
from typing import Iterable, Optional, Set, List
import re
import difflib

# Simple filler words to remove in 'light' mode (conservative)
_FILLERS = {
    "so", "like", "um", "uh", "well", "you know", "i mean",
    "kind of", "sort of", "just", "actually", "basically"
}

_WORD_RE = re.compile(r"\w+|\S")


def build_vocab_from_chunks(chunks: Iterable[str], min_freq: int = 2, max_vocab: int = 10000) -> Set[str]:
    """Build a simple vocabulary (set of lowercased tokens) from chunk texts.

    Keeps words that appear at least `min_freq` times and caps vocab size to `max_vocab` by frequency.
    Intended to be fast and conservative — used only for the `spell` mode.
    """
    freq = {}
    for c in chunks:
        if not c:
            continue
        for w in _WORD_RE.findall(c.lower()):
            if not w.isalpha():
                continue
            freq[w] = freq.get(w, 0) + 1

    # Filter by min_freq and sort by frequency
    items = [(w, f) for w, f in freq.items() if f >= min_freq]
    items.sort(key=lambda x: x[1], reverse=True)
    vocab = {w for w, _ in items[:max_vocab]}
    return vocab


def _light_normalize(q: str) -> str:
    # Lowercase
    s = q.lower()
    # Replace newlines and repeated whitespace with single space
    s = re.sub(r"\s+", " ", s).strip()
    # Remove excessive punctuation (keep sentence punctuation but collapse repeats)
    s = re.sub(r"[""'`]+", '"', s)
    s = re.sub(r"[-]{2,}", "-", s)
    # Remove filler phrases conservatively
    for f in _FILLERS:
        s = re.sub(r"\b" + re.escape(f) + r"\b", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _spell_correct(q: str, vocab: Optional[Set[str]]) -> str:
    if not vocab:
        return q
    words = _WORD_RE.findall(q)
    out_words: List[str] = []
    for w in words:
        # Only attempt to correct alphabetical tokens of reasonable length
        if not w.isalpha() or len(w) <= 3:
            out_words.append(w)
            continue
        lw = w.lower()
        if lw in vocab:
            out_words.append(w)
            continue
        # Find high-confidence close match (conservative cutoff)
        matches = difflib.get_close_matches(lw, vocab, n=1, cutoff=0.86)
        if matches:
            # Preserve original casing for replacement
            replacement = matches[0]
            # If original was capitalized, capitalize replacement
            if w[0].isupper():
                replacement = replacement.capitalize()
            print(f"[SPELL] '{w}' → '{replacement}'")
            out_words.append(replacement)
        else:
            out_words.append(w)
    # Join tokens while preserving spacing roughly (tokens include punctuation)
    return "".join(
        [ (" " + t) if i>0 and re.match(r"\w", t) and re.match(r"\w", (words[i-1] if i-1 < len(words) else "")) else t
          for i, t in enumerate(out_words) ]
    )


def preprocess_query(query: str, mode: str = "none", vocab: Optional[Set[str]] = None) -> str:
    """Preprocess a query according to mode.

    - mode: one of 'none' (noop), 'light', or 'spell'.
    - vocab: optional vocabulary set required for 'spell' mode; if not provided, spell mode is a noop.
    """
    if not query:
        return query
    if mode is None or mode == "none":
        return query
    if mode == "light":
        return _light_normalize(query)
    if mode == "spell":
        # Apply light normalization first, then conservative spell correction
        normalized = _light_normalize(query)
        return _spell_correct(normalized, vocab)
    # Unknown mode: noop
    return query
