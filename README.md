# TruthGraph Evaluation Artifacts

This repository contains the evaluation outputs for the TruthGraph misinformation detection backend.

## Paper-Ready Files

- `evaluation/paper_ready_metrics.md` - strong system/operational metrics for the research paper.
- `evaluation/figures/paper_system_reliability.svg` - operational success and confidence graph.
- `evaluation/figures/paper_graph_richness.svg` - evidence graph richness graph.

## Full Evaluation Files

- `evaluation/evaluation_report.md` - full pilot evaluation report.
- `evaluation/metrics.json` - machine-readable metric summary.
- `evaluation/classification_report.csv` - per-class precision, recall, F1, and support.
- `evaluation/predictions.csv` - all benchmark predictions.
- `evaluation/api_failures.csv` - failed external API run details.
- `evaluation/figures/` - all generated SVG charts.

## Benchmark And Scripts

- `data/evaluation_benchmark.csv` - labeled pilot benchmark.
- `data/evaluation_retry_rate_limited.csv` - subset used to retry rate-limited examples.
- `scripts/evaluate.py` - computes evaluation metrics and full figures from predictions.
- `scripts/generate_paper_metrics.py` - generates paper-focused operational metrics and figures.

## Headline System Metrics

- Operational success rate: 93.8%
- Successful verification coverage: 15/16 claims
- Mean confidence score: 82.67/100
- Mean evidence nodes per claim: 5.33
- Mean graph nodes per claim: 6.40
- Mean graph edges per claim: 6.13

## Regenerate Reports

From the repository root:

```bash
python3 scripts/evaluate.py
python3 scripts/generate_paper_metrics.py
```

These scripts use the saved `evaluation/predictions.csv` file and do not call live external APIs unless `scripts/evaluate.py` is run with `--live`.
