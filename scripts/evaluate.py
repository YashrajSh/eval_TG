from __future__ import annotations

import argparse
import asyncio
import csv
import json
from collections import Counter
from pathlib import Path
from statistics import mean
from time import perf_counter

LABELS = ["true", "false", "misleading", "unverifiable"]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


async def run_live(benchmark: list[dict[str, str]], limit: int | None) -> list[dict[str, str]]:
    from app.models import InputType
    from app.pipeline import VerificationPipeline

    pipeline = VerificationPipeline()
    rows: list[dict[str, str]] = []
    for item in benchmark[:limit] if limit else benchmark:
        start = perf_counter()
        try:
            result = await pipeline.verify(item["input"], InputType(item["type"]))
            latency_ms = round((perf_counter() - start) * 1000, 2)
            evidence_nodes = sum(len(claim.evidence_nodes) for claim in result.claims)
            graph_nodes = sum(len(graph.nodes) for graph in result.evidence_graphs)
            graph_edges = sum(len(graph.edges) for graph in result.evidence_graphs)
            supporting_sources = sum(len(claim.supporting_sources) for claim in result.claims)
            contradicting_sources = sum(len(claim.contradicting_sources) for claim in result.claims)
            predicted = result.overall_verdict
            confidence = result.overall_confidence
            credibility_score = result.credibility_score
            error = ""
            print(f"{item['id']}: {item['ground_truth']} -> {predicted} ({confidence})")
        except Exception as exc:  # noqa: BLE001 - evaluation records failures instead of stopping.
            latency_ms = round((perf_counter() - start) * 1000, 2)
            predicted = "unverifiable"
            confidence = 0
            credibility_score = 0
            evidence_nodes = graph_nodes = graph_edges = supporting_sources = contradicting_sources = 0
            error = str(exc)
            print(f"{item['id']}: ERROR {error}")
        rows.append(
            {
                "id": item["id"],
                "input": item["input"],
                "ground_truth": item["ground_truth"],
                "predicted": predicted,
                "confidence": str(confidence),
                "credibility_score": str(credibility_score),
                "latency_ms": str(latency_ms),
                "evidence_nodes": str(evidence_nodes),
                "graph_nodes": str(graph_nodes),
                "graph_edges": str(graph_edges),
                "supporting_sources": str(supporting_sources),
                "contradicting_sources": str(contradicting_sources),
                "correct": str(item["ground_truth"] == predicted),
                "error": error,
            }
        )
    return rows


def write_predictions(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "id",
        "input",
        "ground_truth",
        "predicted",
        "confidence",
        "credibility_score",
        "latency_ms",
        "evidence_nodes",
        "graph_nodes",
        "graph_edges",
        "supporting_sources",
        "contradicting_sources",
        "correct",
        "error",
    ]
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def load_predictions(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def fnum(row: dict[str, str], key: str) -> float:
    try:
        return float(row[key])
    except (KeyError, ValueError):
        return 0.0


def confusion(rows: list[dict[str, str]]) -> dict[str, dict[str, int]]:
    matrix = {actual: {pred: 0 for pred in LABELS} for actual in LABELS}
    for row in rows:
        matrix[row["ground_truth"]][row["predicted"]] += 1
    return matrix


def div(a: float, b: float) -> float:
    return a / b if b else 0.0


def successful_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [row for row in rows if not row.get("error", "").strip()]


def failed_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [row for row in rows if row.get("error", "").strip()]


def metrics(rows: list[dict[str, str]]) -> dict:
    total_examples = len(rows)
    failures = failed_rows(rows)
    scored_rows = successful_rows(rows)
    matrix = confusion(scored_rows)
    total = len(scored_rows)
    per_class = {}
    for label in LABELS:
        tp = matrix[label][label]
        fp = sum(matrix[a][label] for a in LABELS if a != label)
        fn = sum(matrix[label][p] for p in LABELS if p != label)
        precision = div(tp, tp + fp)
        recall = div(tp, tp + fn)
        f1 = div(2 * precision * recall, precision + recall)
        support = sum(matrix[label].values())
        per_class[label] = {"precision": precision, "recall": recall, "f1": f1, "support": support}
    accuracy = div(sum(row["ground_truth"] == row["predicted"] for row in scored_rows), total)
    macro_precision = mean(v["precision"] for v in per_class.values())
    macro_recall = mean(v["recall"] for v in per_class.values())
    macro_f1 = mean(v["f1"] for v in per_class.values())
    weighted_f1 = div(sum(v["f1"] * v["support"] for v in per_class.values()), total)
    return {
        "total_examples": total_examples,
        "successful_examples": total,
        "failed_examples": len(failures),
        "operational_success_rate": div(total, total_examples),
        "n": total,
        "accuracy": accuracy,
        "macro_precision": macro_precision,
        "macro_recall": macro_recall,
        "macro_f1": macro_f1,
        "weighted_f1": weighted_f1,
        "per_class": per_class,
        "confusion_matrix": matrix,
        "mean_confidence": mean([fnum(row, "confidence") for row in scored_rows]) if scored_rows else 0,
        "mean_latency_ms": mean([fnum(row, "latency_ms") for row in scored_rows]) if scored_rows else 0,
        "mean_evidence_nodes": mean([fnum(row, "evidence_nodes") for row in scored_rows]) if scored_rows else 0,
        "mean_graph_nodes": mean([fnum(row, "graph_nodes") for row in scored_rows]) if scored_rows else 0,
        "mean_graph_edges": mean([fnum(row, "graph_edges") for row in scored_rows]) if scored_rows else 0,
        "ground_truth_distribution": dict(Counter(row["ground_truth"] for row in scored_rows)),
        "prediction_distribution": dict(Counter(row["predicted"] for row in scored_rows)),
    }


def svg(path: Path, body: str, width: int = 760, height: int = 460) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<rect width="100%" height="100%" fill="white"/>
<style>text{{font-family:Arial,Helvetica,sans-serif;fill:#24292f;font-size:13px}} .title{{font-size:18px;font-weight:700}} .small{{font-size:11px}}</style>
{body}
</svg>
""",
        encoding="utf-8",
    )


def chart_overall(m: dict, path: Path) -> None:
    vals = [
        ("Accuracy", m["accuracy"]),
        ("Macro P", m["macro_precision"]),
        ("Macro R", m["macro_recall"]),
        ("Macro F1", m["macro_f1"]),
        ("Weighted F1", m["weighted_f1"]),
    ]
    body = ['<text class="title" x="28" y="34">Overall Evaluation Metrics</text>']
    left, top, h, barw, gap = 86, 74, 270, 86, 28
    for tick in range(0, 101, 20):
        y = top + h - h * tick / 100
        body.append(f'<line x1="{left}" y1="{y}" x2="710" y2="{y}" stroke="#d0d7de"/>')
        body.append(f'<text class="small" x="{left-10}" y="{y+4}" text-anchor="end">{tick/100:.1f}</text>')
    for i, (label, value) in enumerate(vals):
        bh = h * value
        x = left + i * (barw + gap)
        y = top + h - bh
        body.append(f'<rect x="{x}" y="{y}" width="{barw}" height="{bh}" fill="#1565c0"/>')
        body.append(f'<text x="{x+barw/2}" y="{y-7}" text-anchor="middle">{value:.2f}</text>')
        body.append(f'<text class="small" x="{x+barw/2}" y="{top+h+26}" text-anchor="middle">{label}</text>')
    svg(path, "\n".join(body))


def chart_confusion(m: dict, path: Path) -> None:
    matrix = m["confusion_matrix"]
    maxv = max(max(row.values()) for row in matrix.values()) or 1
    left, top, cell = 150, 92, 76
    body = ['<text class="title" x="28" y="34">Confusion Matrix</text>']
    for i, actual in enumerate(LABELS):
        body.append(f'<text x="{left-10}" y="{top+i*cell+43}" text-anchor="end">{actual}</text>')
    for j, pred in enumerate(LABELS):
        body.append(f'<text x="{left+j*cell+cell/2}" y="{top-14}" text-anchor="middle">{pred}</text>')
    for i, actual in enumerate(LABELS):
        for j, pred in enumerate(LABELS):
            v = matrix[actual][pred]
            opacity = 0.15 + 0.75 * v / maxv
            body.append(f'<rect x="{left+j*cell}" y="{top+i*cell}" width="{cell}" height="{cell}" fill="rgba(25,118,210,{opacity:.2f})" stroke="#d0d7de"/>')
            body.append(f'<text x="{left+j*cell+cell/2}" y="{top+i*cell+cell/2+5}" text-anchor="middle" font-weight="700">{v}</text>')
    body.append('<text x="300" y="438">Predicted label</text>')
    body.append('<text transform="translate(24 280) rotate(-90)">Ground truth label</text>')
    svg(path, "\n".join(body), 620, 470)


def chart_per_class(m: dict, path: Path) -> None:
    colors = {"precision": "#1565c0", "recall": "#2e7d32", "f1": "#ef6c00"}
    left, top, h, group = 78, 74, 280, 160
    body = ['<text class="title" x="28" y="34">Per-Class Precision, Recall, and F1</text>']
    for tick in range(0, 101, 20):
        y = top + h - h * tick / 100
        body.append(f'<line x1="{left}" y1="{y}" x2="725" y2="{y}" stroke="#d0d7de"/>')
        body.append(f'<text class="small" x="{left-10}" y="{y+4}" text-anchor="end">{tick/100:.1f}</text>')
    for i, label in enumerate(LABELS):
        for k, key in enumerate(["precision", "recall", "f1"]):
            val = m["per_class"][label][key]
            bh = h * val
            x = left + i * group + 32 + k * 24
            y = top + h - bh
            body.append(f'<rect x="{x}" y="{y}" width="18" height="{bh}" fill="{colors[key]}"/>')
            body.append(f'<text class="small" x="{x+9}" y="{y-4}" text-anchor="middle">{val:.2f}</text>')
        body.append(f'<text x="{left+i*group+64}" y="{top+h+28}" text-anchor="middle">{label}</text>')
    for i, key in enumerate(["precision", "recall", "f1"]):
        body.append(f'<rect x="{510+i*88}" y="28" width="12" height="12" fill="{colors[key]}"/><text class="small" x="{528+i*88}" y="39">{key}</text>')
    svg(path, "\n".join(body), 790, 430)


def chart_confidence(rows: list[dict[str, str]], path: Path) -> None:
    left, top, h, w = 74, 64, 260, 650
    step = w / max(len(rows), 1)
    body = ['<text class="title" x="28" y="34">Confidence by Evaluation Example</text>']
    for tick in range(0, 101, 20):
        y = top + h - h * tick / 100
        body.append(f'<line x1="{left}" y1="{y}" x2="{left+w}" y2="{y}" stroke="#d0d7de"/>')
        body.append(f'<text class="small" x="{left-10}" y="{y+4}" text-anchor="end">{tick}</text>')
    for i, row in enumerate(rows):
        conf = fnum(row, "confidence")
        bh = h * conf / 100
        bw = min(24, step * 0.68)
        x = left + i * step + (step - bw) / 2
        y = top + h - bh
        color = "#2e7d32" if row["ground_truth"] == row["predicted"] else "#c62828"
        body.append(f'<rect x="{x}" y="{y}" width="{bw}" height="{bh}" fill="{color}"/>')
        body.append(f'<text class="small" x="{x+bw/2}" y="{top+h+18}" text-anchor="middle" transform="rotate(45 {x+bw/2} {top+h+18})">{row["id"]}</text>')
    body.append('<rect x="560" y="24" width="12" height="12" fill="#2e7d32"/><text class="small" x="578" y="35">Correct</text>')
    body.append('<rect x="640" y="24" width="12" height="12" fill="#c62828"/><text class="small" x="658" y="35">Incorrect</text>')
    svg(path, "\n".join(body), 800, 420)


def chart_graph_stats(m: dict, path: Path) -> None:
    vals = [
        ("Evidence nodes", m["mean_evidence_nodes"]),
        ("Graph nodes", m["mean_graph_nodes"]),
        ("Graph edges", m["mean_graph_edges"]),
    ]
    maxv = max(v for _, v in vals) or 1
    left, top, h, barw, gap = 110, 70, 260, 120, 60
    body = ['<text class="title" x="28" y="34">Average Evidence Graph Statistics</text>']
    for tick in range(0, int(maxv) + 2):
        y = top + h - h * tick / (maxv + 1)
        body.append(f'<line x1="{left}" y1="{y}" x2="640" y2="{y}" stroke="#d0d7de"/>')
        body.append(f'<text class="small" x="{left-10}" y="{y+4}" text-anchor="end">{tick}</text>')
    for i, (label, value) in enumerate(vals):
        bh = h * value / (maxv + 1)
        x = left + i * (barw + gap)
        y = top + h - bh
        body.append(f'<rect x="{x}" y="{y}" width="{barw}" height="{bh}" fill="#6a1b9a"/>')
        body.append(f'<text x="{x+barw/2}" y="{y-7}" text-anchor="middle">{value:.1f}</text>')
        body.append(f'<text x="{x+barw/2}" y="{top+h+26}" text-anchor="middle">{label}</text>')
    svg(path, "\n".join(body), 700, 420)


def write_outputs(rows: list[dict[str, str]], out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    m = metrics(rows)
    scored_rows = successful_rows(rows)
    failures = failed_rows(rows)
    (out / "metrics.json").write_text(json.dumps(m, indent=2), encoding="utf-8")
    if failures:
        write_predictions(out / "api_failures.csv", failures)
    with (out / "classification_report.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["class", "precision", "recall", "f1", "support"])
        for label in LABELS:
            item = m["per_class"][label]
            writer.writerow([label, f"{item['precision']:.4f}", f"{item['recall']:.4f}", f"{item['f1']:.4f}", item["support"]])
    figs = out / "figures"
    chart_overall(m, figs / "overall_metrics.svg")
    chart_confusion(m, figs / "confusion_matrix.svg")
    chart_per_class(m, figs / "per_class_metrics.svg")
    chart_confidence(scored_rows, figs / "confidence_by_example.svg")
    chart_graph_stats(m, figs / "graph_statistics.svg")
    report = f"""# TruthGraph Evaluation Report

This pilot evaluation uses `data/evaluation_benchmark.csv`, a small labeled benchmark of factual, false, misleading, and unverifiable claims. Classification metrics are computed only on successful API runs; API failures are reported separately as operational reliability. For publication-grade claims, rerun the same script on a larger benchmark dataset.

## Summary Metrics

- Total examples: {m['total_examples']}
- Successful predictions: {m['successful_examples']}
- API failures: {m['failed_examples']}
- Operational success rate: {m['operational_success_rate']:.3f}
- Accuracy: {m['accuracy']:.3f}
- Macro precision: {m['macro_precision']:.3f}
- Macro recall: {m['macro_recall']:.3f}
- Macro F1-score: {m['macro_f1']:.3f}
- Weighted F1-score: {m['weighted_f1']:.3f}
- Mean confidence: {m['mean_confidence']:.2f}/100
- Mean latency: {m['mean_latency_ms']:.2f} ms
- Mean evidence nodes: {m['mean_evidence_nodes']:.2f}
- Mean graph nodes: {m['mean_graph_nodes']:.2f}
- Mean graph edges: {m['mean_graph_edges']:.2f}

## Paper-Ready Text

On the pilot benchmark of {m['total_examples']} labeled claims, TruthGraph completed {m['successful_examples']} successful verification runs, corresponding to an operational success rate of {m['operational_success_rate']:.3f}. Over successful runs, TruthGraph achieved an accuracy of {m['accuracy']:.3f}, macro F1-score of {m['macro_f1']:.3f}, and weighted F1-score of {m['weighted_f1']:.3f}. The system produced an average confidence score of {m['mean_confidence']:.2f}/100. The generated evidence graphs contained an average of {m['mean_graph_nodes']:.2f} nodes and {m['mean_graph_edges']:.2f} edges per example, indicating that verdict generation was supported by structured evidence nodes and relationships rather than only a direct model response.

## Figures

- `figures/overall_metrics.svg`
- `figures/confusion_matrix.svg`
- `figures/per_class_metrics.svg`
- `figures/confidence_by_example.svg`
- `figures/graph_statistics.svg`
"""
    (out / "evaluation_report.md").write_text(report, encoding="utf-8")
    print(json.dumps({k: m[k] for k in ["total_examples", "successful_examples", "failed_examples", "operational_success_rate", "accuracy", "macro_f1", "weighted_f1", "mean_confidence"]}, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", default="data/evaluation_benchmark.csv")
    parser.add_argument("--output-dir", default="evaluation")
    parser.add_argument("--predictions", default=None)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    out = Path(args.output_dir)
    pred_path = Path(args.predictions) if args.predictions else out / "predictions.csv"
    if args.live:
        rows = asyncio.run(run_live(read_csv(Path(args.benchmark)), args.limit))
        write_predictions(pred_path, rows)
    else:
        rows = load_predictions(pred_path)
    write_outputs(rows, out)


if __name__ == "__main__":
    main()
