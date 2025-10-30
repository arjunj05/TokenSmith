# Inspect logged queries and their chunks
import json
from pathlib import Path
log_path = Path("logs/run_20251029_215252.jsonl")
if not log_path.exists():
    raise SystemExit("Log not found: " + str(log_path))

art = Path("index/sections")
prefix = "textbook_index"
chunks = __import__("pickle").load(open(art / f"{prefix}_chunks.pkl","rb"))
meta   = __import__("pickle").load(open(art / f"{prefix}_meta.pkl","rb"))

for line in open(log_path, encoding="utf-8"):
    entry = json.loads(line)
    if entry.get("event") == "query":
        print("==== QUERY ID", entry["query_id"], "====")
        print("Query text:", entry.get("query"))
        # Which candidates were returned?
        cand_idxs = entry.get("retrieval", {}).get("candidate_indices", [])
        if cand_idxs:
            print("Candidate indices:", cand_idxs[:10], "...")
        # The generator selection:
        for c in entry.get("chunks_used", []):
            gi = c["global_index"]
            print(f"rank={c['rank']} idx={gi} | section={meta[gi].get('section')} | preview={c.get('preview')}")
            print(" -> full chunk head:", chunks[gi][:200].replace('\n',' '))
        print("\n")