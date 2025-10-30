import sys
import traceback
from pathlib import Path

# Ensure repo root is importable
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src.retriever import BM25Retriever, FAISSRetriever, load_artifacts

ART_DIR = Path("index/sections")
PREFIX = "textbook_index"
SAMPLE_QUERY = "what is a database"
TOP_K = 5
POOL = 50


def pretty_print(indices, chunks, meta, sources, scores=None):
    for rank, idx in enumerate(indices, 1):
        s = scores.get(idx) if scores else None
        print(f"Rank {rank}: idx={idx} score={s}")
        print(f"  source: {sources[idx]}")
        print(f"  section: {meta[idx].get('section')}")
        preview = (chunks[idx][:300] + '...') if len(chunks[idx]) > 300 else chunks[idx]
        preview_clean = preview.replace("\n", " ")
        print("  preview: " + preview_clean + "\n")


if __name__ == '__main__':
    print("Loading artifacts from", ART_DIR)
    try:
        faiss_index, bm25_index, chunks, sources = load_artifacts(ART_DIR, PREFIX)
        # meta may not be returned by load_artifacts, load explicitly
        import pickle
        meta = pickle.load(open(ART_DIR / f"{PREFIX}_meta.pkl", "rb"))
        print(f"Loaded: faiss_index, bm25_index, {len(chunks)} chunks, {len(sources)} sources, {len(meta)} meta entries")
    except Exception as e:
        print("Failed to load artifacts:")
        traceback.print_exc()
        raise SystemExit(1)

    print("\n--- BM25 retrieval (lexical) ---")
    try:
        bm = BM25Retriever(bm25_index)
        bm_scores = bm.get_scores(SAMPLE_QUERY, POOL, chunks)
        sorted_bm = sorted(bm_scores.items(), key=lambda kv: kv[1], reverse=True)
        top_bm = [idx for idx, _ in sorted_bm[:TOP_K]]
        pretty_print(top_bm, chunks, meta, sources, scores={k: v for k, v in bm_scores.items()})
    except Exception as e:
        print("BM25 retrieval failed:")
        traceback.print_exc()

    print("\n--- FAISS retrieval (semantic) ---")
    try:
        fa = FAISSRetriever(faiss_index, embed_model="Qwen/Qwen3-Embedding-4B")
        fa_scores = fa.get_scores(SAMPLE_QUERY, POOL, chunks)
        sorted_fa = sorted(fa_scores.items(), key=lambda kv: kv[1], reverse=True)
        top_fa = [idx for idx, _ in sorted_fa[:TOP_K]]
        pretty_print(top_fa, chunks, meta, sources, scores={k: v for k, v in fa_scores.items()})
    except Exception as e:
        print("FAISS retrieval failed (likely embedder issue):")
        traceback.print_exc()

    print("\nDone")
