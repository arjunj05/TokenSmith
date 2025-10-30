"""
Lightweight retrieval-only tester that doesn't import FAISS.
Loads pickled chunks/meta/sources from index/sections and runs a small set of queries.
Writes results to scripts/retrieve_quick_results.jsonl
"""
import pickle
from pathlib import Path
import json
import re

ART_DIR = Path("index/sections")
PREFIX = "textbook_index"
OUT = Path("scripts/retrieve_quick_results.jsonl")

QUERIES = [
    ("q1_correct", "Explain what a relational database is and give a short example."),
    ("q1_typo", "Exlain what a relational databse is and give a short exmple."),

    ("q2_1", "What is database normalization and why is it used?"),
    ("q2_2", "How does Third Normal Form (3NF) differ from Boyce-Codd Normal Form (BCNF)?"),

    ("q3_ambig", "What is a transaction?"),
    ("q3_clarify", "In databases, explain ACID transactions briefly."),

    ("q4_clean", "In a distributed database system, how does replication affect consistency and availability? Provide trade-offs and an example."),
    ("q4_noisy", "So I heard about replication and stuff — like in distributed systems, how does replication affect consistency AND availability, and can you give a real world example? I'm trying to understand trade-offs."),

    ("q5_correct", "How do query optimizers estimate the number of distinct values for an attribute?"),
    ("q5_typo", "How do query optimizers estmate the numbr of distinct vales for an attribute?"),

    ("q6_correct", "Define the ACID properties of transactions with a short example for each."),
    ("q6_typo", "Defne the ACID proprties of transactions with a short exmple for each.")
]


def load_artifacts():
    chunks_p = ART_DIR / f"{PREFIX}_chunks.pkl"
    meta_p = ART_DIR / f"{PREFIX}_meta.pkl"
    sources_p = ART_DIR / f"{PREFIX}_sources.pkl"
    bm25_p = ART_DIR / f"{PREFIX}_bm25.pkl"

    chunks = pickle.load(open(chunks_p, "rb"))
    meta = pickle.load(open(meta_p, "rb"))
    sources = pickle.load(open(sources_p, "rb"))

    bm25 = None
    try:
        bm25 = pickle.load(open(bm25_p, "rb"))
    except Exception:
        bm25 = None

    return chunks, meta, sources, bm25


def bm25_topk(bm25_index, query, k=5):
    tokenized = re.sub(r"[^a-z0-9_'#+-]", " ", query.lower()).split()
    try:
        scores = bm25_index.get_scores(tokenized)
    except Exception:
        return []
    import numpy as np
    num = min(len(scores), k)
    idxs = np.argpartition(-scores, kth=num-1)[:num]
    ordered = sorted([(int(i), float(scores[i])) for i in idxs], key=lambda kv: kv[1], reverse=True)
    return ordered


def overlap_topk(chunks, query, k=5):
    qtok = re.sub(r"[^a-z0-9_'#+-]", " ", query.lower()).split()
    scores = []
    for i, ch in enumerate(chunks):
        toks = re.sub(r"[^a-z0-9_'#+-]", " ", ch.lower()).split()
        s = sum(toks.count(t) for t in qtok)
        scores.append((i, float(s)))
    ordered = sorted(scores, key=lambda kv: kv[1], reverse=True)[:k]
    return ordered


if __name__ == '__main__':
    chunks, meta, sources, bm25 = load_artifacts()
    results = []
    print(f"Loaded {len(chunks)} chunks; bm25_loaded={bm25 is not None}")
    for qid, qtext in QUERIES:
        if bm25:
            top = bm25_topk(bm25, qtext, k=5)
        else:
            top = overlap_topk(chunks, qtext, k=5)
        item = {"id": qid, "query": qtext, "topk": []}
        for idx, score in top:
            item["topk"].append({"idx": idx, "score": score, "section": meta[idx].get("section"), "preview": chunks[idx][:300].replace('\n',' ')})
        results.append(item)
    OUT.write_text('\n'.join(json.dumps(x, ensure_ascii=False) for x in results), encoding='utf-8')
    print(f"Wrote results to {OUT}")
