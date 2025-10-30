# Proposal: Query Optimization for Improved RAG Performance

## 1. Overview — what the current implementation does

The project builds a Retrieval-Augmented Generation (RAG) pipeline over a textbook markdown corpus. At a high level it:

- Extracts textbook sections and splits sections into recursive chunks.
- Builds two retrieval artifacts: a lexical BM25 index and a FAISS vector index (embeddings).
- For a chat query, it runs retrieval (FAISS + BM25), fuses scores via an EnsembleRanker (RRF/weighted), optionally applies a segment filter, selects the top-K chunks, and injects them into a generation prompt that is sent to a local llama.cpp model for response generation.
- Session-level instrumentation writes `logs/run_<session>.jsonl` entries that record retrieval candidates, selected chunks (`chunks_used`), and generation outputs.

This pipeline currently does not alter the incoming query (beyond a trivial tokenization for BM25). Retrievers take the raw query string and attempt to find relevant chunks; ranking and reranking operate on retriever outputs.

## 2. Thesis

Small, targeted optimizations to the input query before retrieval can significantly improve retrieval quality and, therefore, the final generated answer. Query-aware preprocessing (normalization, lightweight rewriting, expansion, term weighting, or intent routing) is a low-risk, high-reward intervention point because it: (a) is cheap to implement, (b) improves upstream retrieval signals, and (c) is decoupled from the expensive generation model.

## 3. Identified issues & motivating examples

### ILLUSTRATIVE Example of failure modes
- Typo / orthographic mismatch
  - Query: "whatt is a databse" → BM25 may miss exact matches; embeddings may still find similar vectors but lexical recall suffers.
- Morphology / inflection mismatch
  - Query: "databases indexing" vs index contains "indexing" or "index" variants; stemming/lemmatization could increase hits.
- Long, noisy queries with context
  - Query: "In the context of distributed systems, how does database replication affect consistency and what examples show the trade-offs?" — long phrases can dilute exact-match signals.
  - Metric behavior: MRR lower because the correct definitional section is ranked below longer context sections.
- Ambiguous short queries
  - Query: "transaction" — needs disambiguation (ACID vs financial transaction examples); adding conversational context or intent classification helps.


### What I tested (small pilot)

I ran a focused retrieval-only experiment to validate that the issues noted above actually show up when using TokenSmith. The code used is in:

- `scripts/batch_test.py` — the batch runner that executes retrieval (FAISS + BM25) and optionally generation.
- `scripts/retrieve_test.py` — a small FAISS+BM25 retrieval diagnostic script used during debugging.
- `scripts/compute_batch_metrics.py` — utility I added to compute the stability metrics we report below (top-1 equality and top-5 overlap).

These scripts are included in the repository so others can reproduce the steps and numbers.

### Exact empirical numbers (from the pilot run)

Notes on methodology: we used the predefined query pairs in `scripts/batch_test.py` (typo vs correct pairs, and clean vs noisy pairs). The retrieval-only run produced a `batch_results` JSONL (kept in `scripts/` locally). The metrics below were computed from that run using `scripts/compute_batch_metrics.py`.

Per-pair metrics (Top-1 equality and Top-5 overlap):

- q1_correct vs q1_typo: top-1 equal = True; top-5 overlap = 4 / 5 (0.8)
- q4_clean vs q4_noisy: top-1 equal = False; top-5 overlap = 4 / 5 (0.8)
- q5_correct vs q5_typo: top-1 equal = True; top-5 overlap = 2 / 5 (0.4)
- q6_correct vs q6_typo: top-1 equal = True; top-5 overlap = 3 / 5 (0.6)

Aggregates across these 4 pairs:

- Top-1 equality rate: 0.75 (75%)
- Average top-5 overlap fraction: 0.65

All numbers above were computed directly from the retrieval-only run `scripts/batch_results_20251030_170359.jsonl` using `scripts/compute_batch_metrics.py` and reflect only this small pilot.

### Interpretation

- Top-1: For 3 of 4 query pairs the top-1 retrieved chunk was unchanged by the typo/noise; this suggests partial robustness. However, one pair (q4) changed top-1, which can materially affect the generator's answer.
- Top-5 overlap: on average 65% overlap means re-ranking within the top candidates is frequently affected by noise/typos; this can alter the pool of context the generator sees.

Taken together: the pilot indicates there is an opportunity for simple preprocessing to increase retrieval stability. It is not definitive, but it is a strong signal that further experiments are worthwhile.

### Reproducible code (where to look)

Run the same pilot locally by executing the following (example):

1. Retrieval-only batch (reproduces the `batch_results` used to compute numbers above):

```bash
python3 scripts/batch_test.py --no-gen
```

2. Compute the metrics from the produced `scripts/batch_results_*.jsonl` file:

```bash
python3 scripts/compute_batch_metrics.py --input scripts/batch_results_20251030_170359.jsonl --output scripts/batch_metrics_20251030_170359.json
```

3. If you want to re-run the FAISS diagnostic directly:

```bash
python3 scripts/retrieve_test.py
```


## 4. Specific features to implement (prioritized)

Given the quick pilot, it seems there is room for improvement in TokenSmith to pre-process user queries to reduce the effect of failure cases listed earlier.

My goal for this project is to pick quick wins that are low-risk and measurable, then 1–2 medium-impact experiments.

Quick wins (implement first)
- `preprocess_query(query)` and `bm25_tokenize(query)`
  - Normalize whitespace, lowercasing, and punctuation. Reuse `preprocess_for_bm25()` behavior.
  - Wire into `get_answer()` before calling retrievers. Ensure BM25 retriever uses the same tokenization used at index time.
- Simple typo-tolerant fallback
  - Conservative spell correction (Norvig-style frequency-based or SymSpell) with an option to disable.

Medium (pick 1–2)
- Key-term extraction + term boosting
  - Extract noun phrases/entities and boost BM25 scoring (by duplicating tokens or applying term weights).
- Retrieval-optimized rewrite (small instruction-tuned model)
  - Use a lightweight local model or prompt-based rewrite to clarify/shorten queries before retrieval. Keep the original query for generation.
- Context Continuation Between Queries
  - Feed past questions and responses as context into future questions so users can ask follow up questions.

## 5. Integration plan & engineering contract

Contract (small & testable)
- Inputs: raw user query (string), optional user history/context
- Outputs: normalized query + optional retrieval-optimized rewrite; the pipeline must still return the same generation output shape
- Error modes: any rewrite must be conservative and reversible; changes are toggleable via `config/config.yaml` so experiments can be A/B tested

Where to integrate
- Add `src/preprocessing/query.py` exposing:
  - `preprocess_query(query, mode=...)`
  - `bm25_tokenize(query)`
  - `extract_key_terms(query)` (optional)
- Call `preprocess_query()` in `src/main.get_answer()` before retrievers. Pass both raw and processed queries to retrievers and ranker as needed.
- Add config flags in `config/config.yaml` and expose them via `QueryPlanConfig`.

Testing & metrics
- Unit tests for tokenization & preprocessing in `tests/`
- `scripts/retrieve_test.py` (already present) to sanity-check that preprocessed queries improve top-K retrieval
- `scripts/eval_retrieval.py` to compute P@k and MRR for a set of labeled queries
.

