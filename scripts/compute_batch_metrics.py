"""Compute simple retrieval stability metrics from a batch results JSONL.

Usage:
  python scripts/compute_batch_metrics.py \
      --input scripts/batch_results_20251030_170359.jsonl \
      --output scripts/batch_metrics_20251030_170359.json

This script computes per-pair Top-1 equality and Top-5 overlap fraction and
aggregates (Top-1 equality rate and average Top-5 overlap fraction).

It is intentionally small and dependency-free so others can reproduce results.
"""
import argparse
import json
from pathlib import Path
from datetime import datetime


def load_jsonl(path: Path):
    with path.open(encoding='utf-8') as f:
        for line in f:
            line=line.strip()
            if not line:
                continue
            yield json.loads(line)


def compute_metrics(records, pairs):
    byid = {r['id']: r for r in records}
    results = []
    for a,b in pairs:
        A = byid[a]['topk_idxs']
        B = byid[b]['topk_idxs']
        top1_eq = (A[0]==B[0]) if A and B else False
        top5_A = set(A[:5])
        top5_B = set(B[:5])
        overlap = len(top5_A & top5_B)
        results.append({
            'pair': f"{a} vs {b}",
            'top1_eq': top1_eq,
            'top5_overlap_count': int(overlap),
            'top5_overlap_frac': overlap/5.0,
            'A_top1': int(A[0]) if A else None,
            'B_top1': int(B[0]) if B else None,
        })

    agg_top1 = sum(1 for r in results if r['top1_eq'])/len(results)
    agg_overlap = sum(r['top5_overlap_frac'] for r in results)/len(results)

    return {'pairs': results, 'aggregates': {'top1_equality_rate': agg_top1, 'avg_top5_overlap_frac': agg_overlap}}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', '-i', default='scripts/batch_results_20251030_170359.jsonl')
    parser.add_argument('--output', '-o', default=None)
    args = parser.parse_args()

    inp = Path(args.input)
    if not inp.exists():
        raise SystemExit(f"Input file not found: {inp}")

    records = list(load_jsonl(inp))
    pairs = [('q1_correct','q1_typo'),('q4_clean','q4_noisy'),('q5_correct','q5_typo'),('q6_correct','q6_typo')]
    metrics = compute_metrics(records,pairs)
    out = {
        'generated_at': datetime.utcnow().isoformat()+'Z',
        'input_file': str(inp),
        'metrics': metrics,
    }

    # Print a short human summary to stdout
    print('Per-pair results:')
    for r in metrics['pairs']:
        print(r)
    print('\nAggregates:')
    print(f"Top-1 equality rate: {metrics['aggregates']['top1_equality_rate']:.2f}")
    print(f"Avg top-5 overlap fraction: {metrics['aggregates']['avg_top5_overlap_frac']:.2f}")

    if args.output:
        outp = Path(args.output)
        outp.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding='utf-8')
        print(f"Wrote metrics to: {outp}")


if __name__ == '__main__':
    main()
