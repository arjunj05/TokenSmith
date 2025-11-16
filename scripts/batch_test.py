"""
Batch test runner for query experiments.

Usage:
  python scripts/batch_test.py --model_path /path/to/model.gguf [--queries tests/my_queries.txt] [--no-gen]

Outputs:
  - logs/run_<session>.jsonl will be written by the existing RunLogger (same behavior as chat)
  - scripts/batch_results_<session>.jsonl will contain one JSON object per test query with retrieval and generation details

This script performs retrieval (FAISS+BM25), ranking, selects top_k chunks, and optionally performs generation using the same `answer()` function used by the interactive chat.
"""

import argparse
import json
import sys
from pathlib import Path
import traceback
import queries

def _json_default(o):
    """Fallback JSON serializer: handle numpy scalars/arrays and bytes gracefully."""
    # Try numpy-style .item() for scalars and .tolist() for arrays without
    # forcing a hard dependency on numpy at module import time.
    try:
        if hasattr(o, "item"):
            return o.item()
    except Exception:
        pass
    try:
        if hasattr(o, "tolist"):
            return o.tolist()
    except Exception:
        pass
    if isinstance(o, bytes):
        try:
            return o.decode("utf-8")
        except Exception:
            return str(o)
    # Fallback to string representation
    return str(o)

# Ensure repo root is importable
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from types import SimpleNamespace
from src.config import QueryPlanConfig
from src.instrumentation.logging import init_logger, get_logger
from src.retriever import load_artifacts, FAISSRetriever, BM25Retriever, apply_seg_filter
from src.ranking.ranker import EnsembleRanker
from src.generator import answer
from src.preprocessing.query import preprocess_query, build_vocab_from_chunks




def run_batch(queries, cfg_path: Path, model_path: str = None, no_gen: bool = False, output_dir: Path = Path("."), preproc: str = "none"):
    cfg = QueryPlanConfig.from_yaml(cfg_path)
    init_logger(cfg)
    logger = get_logger()

    # Load artifacts
    artifacts_dir = cfg.make_artifacts_directory()
    faiss_index, bm25_index, chunks, sources = load_artifacts(artifacts_dir=artifacts_dir, index_prefix="textbook_index")

    retrievers = [
        FAISSRetriever(faiss_index, cfg.embed_model),
        BM25Retriever(bm25_index)
    ]
    ranker = EnsembleRanker(ensemble_method=cfg.ensemble_method, weights=cfg.ranker_weights, rrf_k=int(cfg.rrf_k))

    # Build args namespace similar to CLI
    args = SimpleNamespace()
    args.model_path = model_path
    args.system_prompt_mode = cfg.system_prompt_mode

    session_out = output_dir / f"batch_results_{logger.session_id}.jsonl"
    print(f"Writing detailed results to: {session_out}")

    # Build a small vocabulary useful for conservative spell-correction (optional)
    try:
        vocab = build_vocab_from_chunks(chunks)
    except Exception:
        vocab = None

    with open(session_out, "w", encoding="utf-8") as outf:
        # For context tests we will maintain a small conversation history per tag
        history = {}

        for q in queries:
            qid = q["id"]
            text = q["text"]
            tag = q.get("tag", "")

            # If this is a follow-up in a context_test, prepend previous answer as context
            if tag.endswith("followup") and tag.startswith("context_test"):
                # retrieve the last answer for this conversation
                base_tag = "context_test"
                prev_ans = history.get(base_tag)
                if prev_ans:
                    text_for_retrieval = prev_ans + " \nFollowup: " + text
                else:
                    text_for_retrieval = text
            else:
                text_for_retrieval = text

            # Begin query logging
            logger.log_query_start(text)

            # Optionally preprocess the query used for retrieval (default: none)
            preprocessed = text_for_retrieval
            if preproc and preproc != "none":
                try:
                    preprocessed = preprocess_query(text_for_retrieval, mode=preproc, vocab=vocab)
                except Exception:
                    preprocessed = text_for_retrieval

            # Retrieval
            pool_n = max(cfg.pool_size, cfg.top_k + 10)
            raw_scores = {}
            for retr in retrievers:
                try:
                    raw_scores[retr.name] = retr.get_scores(preprocessed, pool_n, chunks)
                except Exception as e:
                    raw_scores[retr.name] = { }

            ordered = ranker.rank(raw_scores=raw_scores)
            topk_idxs = apply_seg_filter(cfg, chunks, ordered)
            logger.log_chunks_used(topk_idxs, chunks, sources)

            ranked_chunks = [chunks[i] for i in topk_idxs]

            gen_text = None
            if not no_gen:
                try:
                    gen_text = answer(text, ranked_chunks, model_path or cfg.model_path, max_tokens=cfg.max_gen_tokens, system_prompt_mode=args.system_prompt_mode)
                except Exception as e:
                    gen_text = None
                    # log the error
                    logger.log_error(e, context=f"generation for {qid}")

            # finalize query log
            logger.log_generation(gen_text or "", {"max_tokens": cfg.max_gen_tokens, "model_path": model_path or cfg.model_path})
            logger.log_query_complete()

            # Save a summary line to output file
            out = {
                "id": qid,
                "query": text,
                "query_for_retrieval": text_for_retrieval,
                "preproc_mode": preproc,
                "preprocessed_query_for_retrieval": preprocessed,
                "candidates_ordered": ordered[:min(len(ordered), pool_n)],
                "topk_idxs": topk_idxs,
                "topk_sections": [ (i, (chunks[i][:200].replace('\n',' '))) for i in topk_idxs ],
                "generation": gen_text
            }
            outf.write(json.dumps(out, ensure_ascii=False, default=_json_default) + "\n")
            outf.flush()

            # store last answer for context tests
            if tag == "context_test" and gen_text:
                history["context_test"] = gen_text

    print("Batch run complete.")
    print(f"Session log: {logger.log_file}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/config.yaml", help="path to yaml config")
    parser.add_argument("--model_path", default=None, help="override model path")
    parser.add_argument("--queries", default=None, help="path to newline-separated queries file (optional) ")
    parser.add_argument("--no-gen", action="store_true", help="skip generation and only test retrieval")
    parser.add_argument("--preproc", choices=["none", "light", "spell"], default="none", help="preprocessing to apply to queries before retrieval")
    args = parser.parse_args()

    if args.queries:
        qlist = []
        p = Path(args.queries)
        for i, line in enumerate(p.read_text(encoding='utf-8').splitlines()):
            if not line.strip():
                continue
            qlist.append({"id": f"q{i+1}", "text": line.strip(), "tag": "batch"})
        queries = qlist
    else:
        queries = queries.MORE_QUERIES #ADDITIONAL_QUERIES #DEFAULT_QUERIES

    run_batch(queries, Path(args.config), model_path=args.model_path, no_gen=args.no_gen, output_dir=Path("scripts"), preproc=args.preproc)
