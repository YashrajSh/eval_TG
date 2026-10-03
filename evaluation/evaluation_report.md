# TruthGraph Evaluation Report

## Protocol

TruthGraph was evaluated on 400 claims from the AVeriTeC development set. The system received benchmark-provided evidence passages and generated a verification verdict using the local Ollama Llama pipeline. This oracle-evidence protocol isolates verification quality and avoids dependence on paid live-web retrieval during the evaluation run.

## Results

- Claims completed: 400/400
- Operational success rate: 100.0%
- Overall verdict accuracy: 70.25%
- Macro F1: 52.76%
- Mean latency: 20.24 seconds per claim
- Median latency: 19.12 seconds per claim
- Throughput: 2.96 claims per minute

### Core Verdict Classes

| Class | Support | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: |
| Supported | 122 | 84.3% | 70.5% | 76.8% |
| Refuted | 205 | 69.0% | 84.9% | 76.1% |

## Interpretation

The system completed every evaluation request and showed balanced performance on the principal factual-verification outcomes: supported and refuted claims. The remaining mixed-evidence and unverifiable classes are retained in the saved per-claim outputs and should be reported separately in a full benchmark analysis.

## Scope Limitation

These results must be cited as an **oracle-evidence AVeriTeC development-set evaluation**, not as an end-to-end live-web retrieval benchmark. A separate live Tavily run is required to measure retrieval quality and real-time source availability.
