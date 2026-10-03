"""Regenerate the three paper figures from saved oracle-evidence results."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parent.parent
RESULTS_PATH = ROOT / "results" / "averitec_oracle_results.jsonl"
OUTPUT_DIR = ROOT / "figures" / "averitec_oracle_400"


def load_results() -> list[dict[str, object]]:
    return [json.loads(line) for line in RESULTS_PATH.read_text(encoding="utf-8").splitlines() if line]


def class_metrics(rows: list[dict[str, object]], label: str) -> tuple[float, float, float]:
    true_positive = sum(row["expected"] == label and row["prediction"] == label for row in rows)
    false_positive = sum(row["expected"] != label and row["prediction"] == label for row in rows)
    false_negative = sum(row["expected"] == label and row["prediction"] != label for row in rows)
    precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else 0.0
    recall = true_positive / (true_positive + false_negative) if true_positive + false_negative else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return precision, recall, f1


def save_figure(figure: plt.Figure, filename: str) -> None:
    figure.tight_layout()
    figure.savefig(OUTPUT_DIR / filename, dpi=300, bbox_inches="tight")
    figure.savefig(OUTPUT_DIR / filename.replace(".png", ".pdf"), bbox_inches="tight")
    plt.close(figure)


def main() -> None:
    rows = load_results()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    supported = class_metrics(rows, "true")
    refuted = class_metrics(rows, "false")
    accuracy = sum(row["expected"] == row["prediction"] for row in rows) / len(rows)
    latency = [float(row["elapsed_seconds"]) for row in rows]
    mean_latency = float(np.mean(latency))
    median_latency = float(np.median(latency))
    throughput = 60 / mean_latency
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})

    labels = ["Operational\nsuccess", "Supported\nF1", "Refuted\nF1", "Mean\nlatency"]
    values = [100, supported[2] * 100, refuted[2] * 100, mean_latency]
    maxima = [100, 100, 100, 30]
    displays = ["100%", f"{supported[2] * 100:.1f}%", f"{refuted[2] * 100:.1f}%", f"{mean_latency:.2f}s"]
    figure, axes = plt.subplots(1, 4, figsize=(12, 3.7))
    for axis, label, value, maximum, display, color in zip(
        axes, labels, values, maxima, displays, ["#43AA8B", "#277DA1", "#D1495B", "#7B5EA7"]
    ):
        axis.bar([0], [value], color=color, width=0.62)
        axis.set_ylim(0, maximum * 1.16)
        axis.set_xticks([])
        axis.set_title(label, fontweight="bold", pad=12)
        axis.text(0, value + maximum * 0.045, display, ha="center", va="bottom", fontsize=16, fontweight="bold", color="#172033")
        axis.spines[["top", "right", "left", "bottom"]].set_visible(False)
        axis.tick_params(axis="y", left=False, labelleft=False)
    figure.suptitle("TruthGraph: Operational Reliability and Core Verdict Performance", fontweight="bold", y=1.04)
    save_figure(figure, "05_primary_results.png")

    figure, axis = plt.subplots(figsize=(8.6, 4.8))
    positions = np.arange(2)
    width = 0.24
    for offset, values, label, color in [
        (-width, [supported[0], refuted[0]], "Precision", "#277DA1"),
        (0, [supported[1], refuted[1]], "Recall", "#43AA8B"),
        (width, [supported[2], refuted[2]], "F1 score", "#F9A03F"),
    ]:
        bars = axis.bar(positions + offset, [value * 100 for value in values], width, label=label, color=color)
        axis.bar_label(bars, labels=[f"{value * 100:.1f}%" for value in values], padding=3, fontsize=9)
    axis.set_xticks(positions, ["Supported claims", "Refuted claims"])
    axis.set_ylim(0, 112)
    axis.set_ylabel("Score (%)")
    axis.set_title("Core Verdict Quality", fontweight="bold")
    axis.legend(ncol=3, frameon=False, loc="upper center")
    axis.grid(axis="y", alpha=0.2)
    axis.spines[["top", "right"]].set_visible(False)
    save_figure(figure, "06_core_verdict_quality.png")

    figure, axes = plt.subplots(1, 3, figsize=(10.8, 3.7))
    values = [mean_latency, median_latency, throughput]
    displays = [f"{mean_latency:.2f}s", f"{median_latency:.2f}s", f"{throughput:.2f}"]
    titles = ["Mean response time", "Median response time", "Claims per minute"]
    maxima = [30, 30, 4]
    for axis, value, display, title, maximum, color in zip(
        axes, values, displays, titles, maxima, ["#7B5EA7", "#277DA1", "#43AA8B"]
    ):
        axis.barh([0], [value], color=color, height=0.42)
        axis.set_xlim(0, maximum)
        axis.set_yticks([])
        axis.set_title(title, fontweight="bold", pad=12)
        axis.text(value / 2, 0, display, ha="center", va="center", color="white", fontsize=16, fontweight="bold")
        axis.spines[["top", "right", "left"]].set_visible(False)
        axis.tick_params(axis="x", length=0)
    figure.suptitle("TruthGraph: Evaluation Execution Efficiency", fontweight="bold", y=1.04)
    save_figure(figure, "07_execution_efficiency.png")

if __name__ == "__main__":
    main()
