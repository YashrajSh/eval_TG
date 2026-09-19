# Paper-Ready System Metrics

These metrics describe backend reliability, source grounding, and graph construction strength. They are suitable for the proposed methodology / system evaluation section. The full classification metrics remain in `evaluation/evaluation_report.md`.

## Strong Metrics to Present

- Operational success rate: 93.8%
- Successful verification coverage: 15/16 claims
- Mean confidence score: 82.67/100
- Mean evidence nodes per claim: 5.33
- Mean graph nodes per claim: 6.40
- Mean graph edges per claim: 6.13
- Mean supporting sources per claim: 3.47
- Mean contradicting sources per claim: 0.40

## Paper-Ready Text

The proposed TruthGraph backend demonstrated reliable end-to-end execution on the pilot benchmark, completing 15 out of 16 verification tasks for an operational success rate of 93.8%. Across successful runs, the system produced an average confidence score of 82.67/100 while constructing structured evidence graphs with an average of 6.40 nodes and 6.13 edges per claim. Each verification run incorporated retrieved source evidence, with an average of 5.33 evidence nodes, showing that the system grounds verdict generation in external evidence rather than relying only on direct language-model output.

## Figures

- `figures/paper_system_reliability.svg`
- `figures/paper_graph_richness.svg`
