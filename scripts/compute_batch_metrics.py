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
    pairs = [
        ('q1_correct', 'q1_typo'),
        ('q2_correct', 'q2_typo'),
        ('q3_correct', 'q3_typo'),
        ('q4_correct', 'q4_typo'),
        ('q5_correct', 'q5_typo'),
        ('q6_correct', 'q6_typo'),
        ('q7_correct', 'q7_typo'),
        ('q8_correct', 'q8_typo'),
        ('q9_correct', 'q9_typo'),
        ('q10_correct', 'q10_typo'),
        ('q11_correct', 'q11_typo'),
        ('q12_correct', 'q12_typo'),
        ('q13_correct', 'q13_typo'),
        ('q14_correct', 'q14_typo'),
        ('q15_correct', 'q15_typo'),
        ('q16_correct', 'q16_typo'),
        ('q17_correct', 'q17_typo'),
        ('q18_correct', 'q18_typo'),
        ('q19_correct', 'q19_typo'),
        ('q20_correct', 'q20_typo'),
        ('q21_correct', 'q21_typo'),
        ('q22_correct', 'q22_typo'),
        ('q23_correct', 'q23_typo'),
        ('q24_correct', 'q24_typo'),
        ('q25_correct', 'q25_typo'),
        ('q26_correct', 'q26_typo'),
        ('q27_correct', 'q27_typo'),
        ('q28_correct', 'q28_typo'),
        ('q29_correct', 'q29_typo'),
        ('q30_correct', 'q30_typo'),
        ('q31_correct', 'q31_typo'),
        ('q32_correct', 'q32_typo'),
        ('q33_correct', 'q33_typo'),
        ('q34_correct', 'q34_typo'),
        ('q35_correct', 'q35_typo'),
        ('q36_correct', 'q36_typo'),
        ('q37_correct', 'q37_typo'),
        ('q38_correct', 'q38_typo'),
        ('q39_correct', 'q39_typo'),
        ('q40_correct', 'q40_typo'),
        ('q41_correct', 'q41_typo'),
        ('q42_correct', 'q42_typo'),
        ('q43_correct', 'q43_typo'),
        ('q44_correct', 'q44_typo'),
        ('q45_correct', 'q45_typo'),
        ('q46_correct', 'q46_typo'),
        ('q47_correct', 'q47_typo'),
        ('q48_correct', 'q48_typo'),
        ('q49_correct', 'q49_typo'),
        ('q50_correct', 'q50_typo'),
    ]

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
