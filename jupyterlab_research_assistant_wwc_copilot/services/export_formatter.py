"""Export formatters for library data."""

import csv
import io
from typing import Optional


class ExportFormatter:
    """Format papers for export in various formats."""

    @staticmethod
    def to_json(papers: list[dict]) -> str:
        """
        Format papers as JSON.

        Args:
            papers: List of paper dictionaries

        Returns:
            JSON string
        """
        import json  # noqa: PLC0415

        return json.dumps(papers, indent=2)

    @staticmethod
    def to_csv(papers: list[dict]) -> str:
        """
        Format papers as CSV.

        Args:
            papers: List of paper dictionaries

        Returns:
            CSV string
        """
        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=[
                "id",
                "title",
                "authors",
                "year",
                "doi",
                "citation_count",
                "abstract",
            ],
        )
        writer.writeheader()
        for paper in papers:
            row = {
                "id": paper.get("id", ""),
                "title": paper.get("title", ""),
                "authors": ", ".join(paper.get("authors", [])),
                "year": paper.get("year", ""),
                "doi": paper.get("doi", ""),
                "citation_count": paper.get("citation_count", ""),
                "abstract": (paper.get("abstract", "") or "")[:500],  # Truncate
            }
            writer.writerow(row)

        return output.getvalue()

    @staticmethod
    def to_bibtex(papers: list[dict]) -> str:
        """
        Format papers as BibTeX.

        Args:
            papers: List of paper dictionaries

        Returns:
            BibTeX string
        """
        entries = []
        for paper in papers:
            # Generate citation key from first author and year
            authors = paper.get("authors", [])
            year = paper.get("year", "unknown")
            first_author = authors[0].split()[-1].lower() if authors else "unknown"
            citation_key = f"{first_author}{year}"

            # Determine entry type (default to @article)
            entry_type = "@article"

            entry = f"{entry_type}{{{citation_key},\n"
            entry += f"  title = {{{paper.get('title', '')}}},\n"

            if authors:
                entry += f"  author = {{{' and '.join(authors)}}},\n"

            if year:
                entry += f"  year = {{{year}}},\n"

            if paper.get("doi"):
                entry += f"  doi = {{{paper.get('doi')}}},\n"

            if paper.get("abstract"):
                # Escape special characters for BibTeX
                abstract = (
                    paper.get("abstract", "").replace("{", "\\{").replace("}", "\\}")
                )
                entry += f"  abstract = {{{abstract[:200]}...}},\n"

            entry += "}\n"
            entries.append(entry)

        return "\n".join(entries)

    @staticmethod
    def export_meta_analysis_csv(
        meta_analysis_result: dict, studies: list[dict]
    ) -> str:
        """
        Export meta-analysis results as CSV.

        Args:
            meta_analysis_result: Meta-analysis result dictionary with pooled effect, CI, etc.
            studies: List of study dictionaries with effect sizes and CIs

        Returns:
            CSV string
        """
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(
            [
                "Study",
                "Effect Size (d)",
                "Standard Error",
                "95% CI Lower",
                "95% CI Upper",
                "Weight (%)",
            ]
        )

        # Write individual studies
        for study in studies:
            writer.writerow(
                [
                    study.get("study_label", ""),
                    f"{study.get('effect_size', 0):.3f}",
                    f"{study.get('std_error', 0):.3f}",
                    f"{study.get('ci_lower', 0):.3f}",
                    f"{study.get('ci_upper', 0):.3f}",
                    f"{study.get('weight', 0) * 100:.1f}",
                ]
            )

        # Write pooled effect row
        writer.writerow([])  # Empty row
        writer.writerow(
            [
                "Pooled Effect",
                f"{meta_analysis_result.get('pooled_effect', 0):.3f}",
                "",
                f"{meta_analysis_result.get('ci_lower', 0):.3f}",
                f"{meta_analysis_result.get('ci_upper', 0):.3f}",
                "",
            ]
        )

        # Write summary statistics
        writer.writerow([])  # Empty row
        writer.writerow(["Summary Statistics", "", "", "", "", ""])
        writer.writerow(
            [
                "I² (Heterogeneity)",
                f"{meta_analysis_result.get('i_squared', 0):.1f}%",
                "",
                "",
                "",
                "",
            ]
        )
        writer.writerow(
            [
                "Tau²",
                f"{meta_analysis_result.get('tau_squared', 0):.3f}",
                "",
                "",
                "",
                "",
            ]
        )
        writer.writerow(
            [
                "Q Statistic",
                f"{meta_analysis_result.get('q_statistic', 0):.3f}",
                "",
                "",
                "",
                "",
            ]
        )
        writer.writerow(
            [
                "Q p-value",
                f"{meta_analysis_result.get('q_p_value', 0):.4f}",
                "",
                "",
                "",
                "",
            ]
        )
        writer.writerow(
            ["P-value", f"{meta_analysis_result.get('p_value', 0):.4f}", "", "", "", ""]
        )

        return output.getvalue()

    @staticmethod
    def export_synthesis_markdown(
        meta_analysis_result: Optional[dict],
        conflict_result: Optional[dict],
        papers: list[dict],
        include_meta_analysis: bool = True,
        include_conflicts: bool = True,
        _include_wwc_assessments: bool = False,
    ) -> str:
        """
        Export synthesis report as Markdown.

        Args:
            meta_analysis_result: Meta-analysis result dictionary (optional)
            conflict_result: Conflict detection result dictionary (optional)
            papers: List of paper dictionaries
            include_meta_analysis: Whether to include meta-analysis section
            include_conflicts: Whether to include conflict detection section
            _include_wwc_assessments: Whether to include WWC assessments (not implemented yet)

        Returns:
            Markdown string
        """
        from datetime import datetime, timezone  # noqa: PLC0415

        lines = []
        lines.append("# Synthesis Report")
        lines.append(
            f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}"
        )
        lines.append(f"**Number of Studies:** {len(papers)}")
        lines.append("")

        # Introduction
        lines.append("## Introduction")
        lines.append("This report presents a synthesis of multiple studies.")
        lines.append("")

        # Methods
        lines.append("## Methods")
        if include_meta_analysis:
            lines.append(
                "- **Meta-Analysis**: Random-effects model using DerSimonian-Laird estimator"
            )
        if include_conflicts:
            lines.append(
                "- **Conflict Detection**: Natural Language Inference (NLI) model"
            )
        lines.append("")

        # Results
        lines.append("## Results")
        lines.append("")

        # Meta-Analysis Section
        if include_meta_analysis and meta_analysis_result:
            lines.append("### Meta-Analysis")
            lines.append("")
            pooled_effect = meta_analysis_result.get("pooled_effect", 0)
            ci_lower = meta_analysis_result.get("ci_lower", 0)
            ci_upper = meta_analysis_result.get("ci_upper", 0)
            i_squared = meta_analysis_result.get("i_squared", 0)

            lines.append(
                f"**Pooled Effect Size:** d = {pooled_effect:.3f} (95% CI: [{ci_lower:.3f}, {ci_upper:.3f}])"
            )
            lines.append(f"**Heterogeneity (I²):** {i_squared:.1f}%")
            if meta_analysis_result.get("heterogeneity_interpretation"):
                lines.append(
                    f"  - {meta_analysis_result['heterogeneity_interpretation']}"
                )
            lines.append(f"**P-value:** {meta_analysis_result.get('p_value', 0):.4f}")
            lines.append("")

            # Forest plot reference
            if meta_analysis_result.get("forest_plot"):
                lines.append("**Forest Plot:** [See embedded image below]")
                lines.append("")
                lines.append(
                    f"![Forest Plot](data:image/png;base64,{meta_analysis_result['forest_plot']})"
                )
                lines.append("")

            # Individual studies table
            lines.append("#### Individual Studies")
            lines.append("")
            lines.append("| Study | Effect Size (d) | 95% CI | Weight (%) |")
            lines.append("|-------|----------------|--------|------------|")
            for study in meta_analysis_result.get("studies", []):
                lines.append(
                    f"| {study.get('study_label', '')} | "
                    f"{study.get('effect_size', 0):.3f} | "
                    f"[{study.get('ci_lower', 0):.3f}, {study.get('ci_upper', 0):.3f}] | "
                    f"{study.get('weight', 0) * 100:.1f} |"
                )
            lines.append("")

        # Conflict Detection Section
        if include_conflicts and conflict_result:
            lines.append("### Conflict Detection")
            lines.append("")
            lines.append(
                f"**Number of Contradictions Found:** {conflict_result.get('n_contradictions', 0)}"
            )
            lines.append("")

            if conflict_result.get("contradictions"):
                lines.append("#### Contradictions")
                lines.append("")
                for i, contradiction in enumerate(conflict_result["contradictions"], 1):
                    lines.append(
                        f"**Contradiction #{i}** (Confidence: {contradiction.get('confidence', 0) * 100:.1f}%)"
                    )
                    if contradiction.get("paper1_title") and contradiction.get(
                        "paper2_title"
                    ):
                        lines.append(f"- **Paper 1:** {contradiction['paper1_title']}")
                        lines.append(f"- **Paper 2:** {contradiction['paper2_title']}")
                    lines.append(
                        f"- **Finding 1:** {contradiction.get('finding1', '')}"
                    )
                    lines.append(
                        f"- **Finding 2:** {contradiction.get('finding2', '')}"
                    )
                    lines.append("")
            else:
                lines.append("No contradictions detected.")
                lines.append("")

        # References
        lines.append("## References")
        lines.append("")
        for i, paper in enumerate(papers, 1):
            authors = ", ".join(paper.get("authors", []))
            year = paper.get("year", "")
            title = paper.get("title", "")
            doi = paper.get("doi", "")
            lines.append(f"{i}. {authors} ({year}). {title}")
            if doi:
                lines.append(f"   DOI: {doi}")
            lines.append("")

        return "\n".join(lines)
