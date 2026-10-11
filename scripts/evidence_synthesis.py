#!/usr/bin/env python3
"""
Evidence Synthesizer: Build evidence matrix and calculate confidence scores.

Takes extracted evidence from all papers, builds RQ × paper × finding matrix,
and calculates confidence based on quality + agreement across papers.

Usage:
    python scripts/evidence_synthesis.py \
        --extractions automation/extracted_evidence/*.json \
        --output automation/processed/evidence_matrix.json
"""

import json
from collections import defaultdict
from glob import glob
from pathlib import Path
from typing import Annotated, Any

import typer

app = typer.Typer(help="Synthesize evidence across papers", add_completion=False, pretty_exceptions_enable=False)

DEFAULT_OUTPUT = Path("automation/processed/evidence_matrix.json")


class EvidenceSynthesizer:
    """Synthesize evidence across papers into confidence scores."""

    def __init__(self):
        self.papers: dict[str, dict] = {}
        self.evidence_matrix: dict[str, Any] = defaultdict(dict)

    def load_evidence(self, extraction_files: list[Path]) -> None:
        """Load extracted evidence from JSON files."""
        for filepath in extraction_files:
            with open(filepath) as f:
                evidence = json.load(f)
            paper_name = evidence["paper_name"]
            self.papers[paper_name] = evidence
            print(f"✅ Loaded: {paper_name}")

    def synthesize_rq1(self) -> dict[str, Any]:
        """RQ1: Is quantum-inspired + P-systems novel?"""
        supporting = []
        contradicting = []

        for name, paper in self.papers.items():
            if paper.get("rq1_combines_quantum_psys"):
                supporting.append(name)
            else:
                contradicting.append(name)

        # Confidence: if NO papers found prior work, confidence is HIGH
        confidence = "high" if len(contradicting) == 0 else "medium"

        return {
            "rq": "RQ1: Is quantum-inspired + P-systems novel?",
            "finding": "No prior work combines quantum-inspired with P-systems",
            "supporting_papers": supporting,
            "contradicting_papers": contradicting,
            "confidence": confidence,
            "quality_weighted_score": sum(self.papers[p].get("quality_total", 0) for p in supporting),
        }

    def synthesize_rq2(self) -> dict[str, Any]:
        """RQ2: What causes dimensionality collapse?"""
        discussing = []
        root_causes = defaultdict(int)

        for name, paper in self.papers.items():
            if paper.get("rq2_discusses_collapse"):
                discussing.append(name)
                if paper.get("rq2_root_cause"):
                    root_causes[paper["rq2_root_cause"]] += 1

        # Most common root cause
        top_cause = max(root_causes.items(), key=lambda x: x[1])[0] if root_causes else "Unknown"

        # Confidence: 3+ papers discussing = high
        confidence = "high" if len(discussing) >= 3 else "medium" if len(discussing) >= 1 else "low"

        return {
            "rq": "RQ2: What causes dimensionality collapse?",
            "finding": f"Dimensionality collapse at D>30 caused by: {top_cause}",
            "supporting_papers": discussing,
            "consensus_root_cause": top_cause,
            "confidence": confidence,
            "quality_weighted_score": sum(self.papers[p].get("quality_total", 0) for p in discussing),
        }

    def synthesize_rq3(self) -> dict[str, Any]:
        """RQ3: What adaptive strategies exist?"""
        all_mechanisms = defaultdict(int)
        supporting_papers = defaultdict(list)

        for name, paper in self.papers.items():
            for mechanism in paper.get("rq3_adaptive_mechanisms", []):
                all_mechanisms[mechanism] += 1
                supporting_papers[mechanism].append(name)

        # Confidence: mechanisms mentioned 3+ times = high
        mechanisms_high_conf = [m for m, count in all_mechanisms.items() if count >= 3]
        confidence = "high" if mechanisms_high_conf else "medium"

        return {
            "rq": "RQ3: What adaptive strategies exist?",
            "finding": "Key adaptive strategies: " + ", ".join(sorted(all_mechanisms.keys())),
            "mechanisms": {m: {"count": c, "papers": supporting_papers[m]} for m, c in all_mechanisms.items()},
            "confidence": confidence,
            "quality_weighted_score": sum(self.papers[p].get("quality_total", 0) for p in self.papers.keys()),
        }

    def synthesize_rq4(self) -> dict[str, Any]:
        """RQ4: What's the GA baseline on CEC2017?"""
        baseline_papers = []
        all_baselines = defaultdict(list)

        for name, paper in self.papers.items():
            if paper.get("rq4_cec2017_baseline"):
                baseline_papers.append(name)
                for func, results in paper.get("rq4_ga_results", {}).items():
                    all_baselines[func].append(results)

        # Average across papers
        averaged_baselines = {}
        for func, results_list in all_baselines.items():
            if results_list and isinstance(results_list[0], dict):
                means = [r.get("mean") for r in results_list if isinstance(r, dict) and r.get("mean")]
                if means:
                    averaged_baselines[func] = {"mean": sum(means) / len(means)}

        confidence = "high" if len(baseline_papers) >= 2 else "medium" if baseline_papers else "low"

        return {
            "rq": "RQ4: What's the GA baseline on CEC2017?",
            "finding": f"GA baseline from {len(baseline_papers)} papers: {averaged_baselines}",
            "supporting_papers": baseline_papers,
            "averaged_results": averaged_baselines,
            "confidence": confidence,
            "quality_weighted_score": sum(self.papers[p].get("quality_total", 0) for p in baseline_papers),
        }

    def synthesize_rq5(self) -> dict[str, Any]:
        """RQ5: Does QIPS scale to high-D?"""
        high_d_papers = []
        scalability_trends = defaultdict(int)

        for name, paper in self.papers.items():
            if paper.get("rq5_high_d_tested"):
                high_d_papers.append(name)
                if paper.get("rq5_scalability_trend"):
                    scalability_trends[paper["rq5_scalability_trend"]] += 1

        # Most common trend
        top_trend = max(scalability_trends.items(), key=lambda x: x[1])[0] if scalability_trends else "Unknown"

        confidence = "medium" if high_d_papers else "low"

        return {
            "rq": "RQ5: Does QIPS scale better to high-D?",
            "finding": f"High-D performance trend: {top_trend}",
            "supporting_papers": high_d_papers,
            "scalability_consensus": top_trend,
            "confidence": confidence,
            "quality_weighted_score": sum(self.papers[p].get("quality_total", 0) for p in high_d_papers),
        }

    def synthesize_all(self) -> dict[str, Any]:
        """Synthesize all RQs into final evidence matrix."""
        return {
            "metadata": {
                "total_papers": len(self.papers),
                "paper_names": list(self.papers.keys()),
                "synthesis_method": "quality-weighted consensus",
            },
            "evidence": {
                "RQ1_novelty": self.synthesize_rq1(),
                "RQ2_collapse": self.synthesize_rq2(),
                "RQ3_adaptation": self.synthesize_rq3(),
                "RQ4_baseline": self.synthesize_rq4(),
                "RQ5_scalability": self.synthesize_rq5(),
            },
        }

    def export(self, output_path: Path) -> None:
        """Export synthesis to JSON."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        synthesis = self.synthesize_all()
        with open(output_path, "w") as f:
            json.dump(synthesis, f, indent=2)
        print(f"\n✅ Synthesis exported: {output_path}")
        print(f"   Papers analyzed: {synthesis['metadata']['total_papers']}")
        for rq_key, rq_data in synthesis["evidence"].items():
            print(f"   {rq_key}: {rq_data['confidence']} confidence")


class NoExtractionsError(ValueError):
    """The extraction pattern matched no files."""


def collect_extraction_files(pattern: str) -> list[Path]:
    """Expand a glob pattern into extraction files. Raises NoExtractionsError when nothing matches."""
    files = [Path(f) for f in glob(pattern)]
    if not files:
        raise NoExtractionsError(pattern)
    return files


@app.command()
def main(
    extractions: Annotated[
        str,
        typer.Option(
            "--extractions",
            help="Pattern for extraction JSON files (e.g., automation/extracted_evidence/*.json)",
        ),
    ],
    output: Annotated[Path, typer.Option("--output", help="Output path for synthesis")] = DEFAULT_OUTPUT,
) -> None:
    """Synthesize evidence across papers into a confidence-scored matrix."""
    try:
        extraction_files = collect_extraction_files(extractions)
    except NoExtractionsError as exc:
        typer.echo(f"❌ No extraction files found matching: {exc}")
        raise typer.Exit(code=1) from exc

    typer.echo("📊 Evidence Synthesizer")
    typer.echo(f"   Loading {len(extraction_files)} extraction files...")

    synthesizer = EvidenceSynthesizer()
    synthesizer.load_evidence(extraction_files)
    synthesizer.export(output)


if __name__ == "__main__":
    app()
