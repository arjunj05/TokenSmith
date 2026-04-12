"""
chunk_selector.py

Budget-aware joint chunk selection for RAG context construction.

Instead of forwarding the top-k reranked chunks directly to the LLM, this
module selects the best *set* of chunks under a fixed token budget.  Each
candidate is scored by three things jointly:

  1. Relevance  – how well the chunk answers the query (from the reranker)
  2. Novelty    – how much new information it adds relative to already-selected
                  chunks (penalises semantic redundancy via cosine similarity
                  on FAISS-stored embeddings)
  3. Efficiency – utility per token cost (shorter chunks that add new info are
                  preferred over long chunks that repeat what is already there)

Selection is greedy: at each step, add the candidate with the highest
marginal utility / token cost until the budget is exhausted.

This is inspired by buffer-pool admission control in database systems: not
every retrieved page (chunk) deserves scarce fast-memory (context window)
space, and the admission policy should consider the value of what is already
buffered.
"""

from __future__ import annotations

from typing import List, Tuple, Optional

import numpy as np


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _token_count(text: str) -> int:
    """Approximate token count from character length (chars / 4)."""
    return max(1, len(text) // 4)


def _cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity between two 1-D numpy vectors."""
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


def _normalize_scores(scores: List[float]) -> List[float]:
    """Min-max normalize a list of floats to [0, 1]."""
    if not scores:
        return scores
    lo, hi = min(scores), max(scores)
    span = hi - lo
    if span == 0:
        return [1.0] * len(scores)
    return [(s - lo) / span for s in scores]


# ---------------------------------------------------------------------------
# Main selection function
# ---------------------------------------------------------------------------

def select_chunks(
    ranked_chunks,
    text_to_chunk_idx: dict,
    faiss_index,
    token_budget: int,
    lam: float = 0.5,
) -> list:
    """
    Greedily select the best subset of chunks under a token budget.

    Parameters
    ----------
    ranked_chunks : List[str] or List[Tuple[str, float]]
        Chunks after reranking.  Each element is either a plain string or a
        (text, score) tuple coming from the cross-encoder reranker.
    text_to_chunk_idx : dict
        Mapping from chunk text to its integer index in the global chunks list.
        Built before reranking so we can recover indices afterwards.
    faiss_index : faiss.Index
        The FAISS index that stores per-chunk embeddings.  Used to compute
        semantic similarity between candidate chunks without re-embedding.
    token_budget : int
        Maximum number of tokens the selected context may contain.
    lam : float
        Trade-off between relevance and novelty.
        lam = 1.0  → pure relevance (ignores redundancy)
        lam = 0.0  → pure novelty  (ignores relevance scores)
        lam = 0.5  → balanced (default)

    Returns
    -------
    List[str] or List[Tuple[str, float]]
        Selected chunks in the same format as the input (str or tuple).
    """
    if not ranked_chunks:
        return ranked_chunks

    is_tuple_format = isinstance(ranked_chunks[0], tuple)

    # Normalise to (text, raw_score) pairs
    if is_tuple_format:
        pairs = [(text, score) for text, score in ranked_chunks]
    else:
        pairs = [(text, 1.0) for text in ranked_chunks]

    # Normalise relevance scores to [0, 1] so they are comparable to cosine sim
    raw_scores = [s for _, s in pairs]
    norm_scores = _normalize_scores(raw_scores)
    candidates = [
        (text, norm_score, text_to_chunk_idx.get(text, -1))
        for (text, _), norm_score in zip(pairs, norm_scores)
    ]

    # Pre-fetch embeddings for all candidates from the FAISS index.
    # faiss.Index.reconstruct(i) returns the stored vector for chunk i.
    # Fall back to None if the index type doesn't support reconstruct.
    def _get_embedding(chunk_idx: int) -> Optional[np.ndarray]:
        if chunk_idx < 0:
            return None
        try:
            vec = faiss_index.reconstruct(chunk_idx)
            return np.array(vec, dtype=np.float32)
        except Exception:
            return None

    # Greedy selection loop
    selected_texts: List[str] = []
    selected_embeddings: List[np.ndarray] = []
    remaining_budget = token_budget

    while candidates:
        best_idx = -1
        best_marginal = -float("inf")

        for i, (text, relevance, chunk_idx) in enumerate(candidates):
            cost = _token_count(text)
            if cost > remaining_budget:
                continue  # doesn't fit; skip

            # Redundancy penalty: max cosine similarity to any already-selected chunk
            embedding = _get_embedding(chunk_idx)
            if embedding is not None and selected_embeddings:
                redundancy = max(
                    _cosine_sim(embedding, sel_emb)
                    for sel_emb in selected_embeddings
                )
            else:
                # No embeddings available or first selection: no penalty
                redundancy = 0.0

            # Marginal utility per token
            marginal = (lam * relevance - (1.0 - lam) * redundancy) / cost
            if marginal > best_marginal:
                best_marginal = marginal
                best_idx = i

        if best_idx == -1:
            # Nothing fits in the remaining budget
            break

        text, _, chunk_idx = candidates.pop(best_idx)
        selected_texts.append(text)
        emb = _get_embedding(chunk_idx)
        if emb is not None:
            selected_embeddings.append(emb)
        remaining_budget -= _token_count(text)

    # Return in the same format as the input
    if is_tuple_format:
        score_map = {text: score for text, score in pairs}
        return [(text, score_map[text]) for text in selected_texts]
    else:
        return selected_texts
