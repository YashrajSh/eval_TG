# TruthGraph Evaluation Report

This pilot evaluation uses `data/evaluation_benchmark.csv`, a small labeled benchmark of factual, false, misleading, and unverifiable claims. Classification metrics are computed only on successful API runs; API failures are reported separately as operational reliability. For publication-grade claims, rerun the same script on a larger benchmark dataset.

## Summary Metrics

- Total examples: 16
- Successful predictions: 15
- API failures: 1
- Operational success rate: 0.938
- Accuracy: 0.333
- Macro precision: 0.333
- Macro recall: 0.333
- Macro F1-score: 0.250
- Weighted F1-score: 0.233
- Mean confidence: 82.67/100
- Mean latency: 12748.14 ms
- Mean evidence nodes: 5.33
- Mean graph nodes: 6.40
- Mean graph edges: 6.13

## Paper-Ready Text

On the pilot benchmark of 16 labeled claims, TruthGraph completed 15 successful verification runs, corresponding to an operational success rate of 0.938. Over successful runs, TruthGraph achieved an accuracy of 0.333, macro F1-score of 0.250, and weighted F1-score of 0.233. The system produced an average confidence score of 82.67/100. The generated evidence graphs contained an average of 6.40 nodes and 6.13 edges per example, indicating that verdict generation was supported by structured evidence nodes and relationships rather than only a direct model response.

## Figures

- `figures/overall_metrics.svg`
- `figures/confusion_matrix.svg`
- `figures/per_class_metrics.svg`
- `figures/confidence_by_example.svg`
- `figures/graph_statistics.svg`
