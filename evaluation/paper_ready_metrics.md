# Paper-Ready Evaluation Metrics

## Recommended Results To Present

| Metric | Result |
| --- | ---: |
| Evaluation claims | 400 |
| Operational success rate | 100.0% |
| Overall verdict accuracy | 70.25% |
| Supported-claim F1 | 76.8% |
| Refuted-claim F1 | 76.1% |
| Mean response time | 20.24 s |
| Median response time | 19.12 s |
| Throughput | 2.96 claims/minute |

## Paper Text

On a 400-claim AVeriTeC development-set evaluation with benchmark-provided evidence, TruthGraph completed all verification requests, yielding a 100.0% operational success rate. The system achieved 70.25% overall verdict accuracy. For the primary factual-verification classes, it achieved F1 scores of 76.8% for supported claims and 76.1% for refuted claims. The mean end-to-end verification time was 20.24 seconds per claim, with a median of 19.12 seconds.

## Required Evaluation Label

Use the phrase **“oracle-evidence evaluation”** in the paper. Evidence passages were supplied from the AVeriTeC benchmark, so this result measures the verification pipeline rather than real-time web retrieval performance.

## Figures

- `figures/averitec_oracle_400/05_primary_results.png`
- `figures/averitec_oracle_400/06_core_verdict_quality.png`
- `figures/averitec_oracle_400/07_execution_efficiency.png`
