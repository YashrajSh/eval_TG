# TruthGraph Evaluation Artifacts

This repository contains the current evaluation artifacts for the TruthGraph misinformation-detection backend.

## Current Evaluation

The published result is a 400-claim AVeriTeC development-set evaluation using benchmark-provided evidence passages and local Ollama inference. This is an **oracle-evidence evaluation**: it evaluates the claim-verification and verdict pipeline without incurring paid live-search costs. It does not measure live Tavily retrieval quality.

### Headline Results

- Claims completed: 400/400
- Operational success rate: 100.0%
- Overall verdict accuracy: 70.25%
- Supported-claim F1: 76.8%
- Refuted-claim F1: 76.1%
- Mean per-claim latency: 20.24 seconds

## Paper Figures

- `evaluation/figures/averitec_oracle_400/05_primary_results.png` - operational reliability and primary verdict performance.
- `evaluation/figures/averitec_oracle_400/06_core_verdict_quality.png` - precision, recall, and F1 for supported and refuted claims.
- `evaluation/figures/averitec_oracle_400/07_execution_efficiency.png` - latency and throughput.

PDF versions are included beside each PNG for direct paper insertion.

## Reproducibility

- `evaluation/results/averitec_oracle_results.jsonl` - 400 per-claim outputs used to calculate the metrics.
- `evaluation/metrics.json` - machine-readable summary.
- `evaluation/scripts/generate_oracle_figures.py` - regenerates the figures from the saved results.

Run from the repository root with Python 3.11+ and Matplotlib installed:

```bash
python evaluation/scripts/generate_oracle_figures.py
```

The chart script expects the results file at `evaluation/results/averitec_oracle_results.jsonl` and writes figures to `evaluation/figures/averitec_oracle_400/`.
