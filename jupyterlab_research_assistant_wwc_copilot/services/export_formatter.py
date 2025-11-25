"""Export formatters for library data."""

import csv
import io
from typing import List, Dict


class ExportFormatter:
    """Format papers for export in various formats."""

    @staticmethod
    def to_json(papers: List[Dict]) -> str:
        """
        Format papers as JSON.

        Args:
            papers: List of paper dictionaries

        Returns:
            JSON string
        """
        import json
        return json.dumps(papers, indent=2)

    @staticmethod
    def to_csv(papers: List[Dict]) -> str:
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
                "abstract"
            ]
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
                "abstract": (paper.get("abstract", "") or "")[:500]  # Truncate
            }
            writer.writerow(row)

        return output.getvalue()

    @staticmethod
    def to_bibtex(papers: List[Dict]) -> str:
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
            first_author = (
                authors[0].split()[-1].lower() if authors else "unknown"
            )
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
                    paper.get("abstract", "")
                    .replace("{", "\\{")
                    .replace("}", "\\}")
                )
                entry += f"  abstract = {{{abstract[:200]}...}},\n"

            entry += "}\n"
            entries.append(entry)

        return "\n".join(entries)

