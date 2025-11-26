"""Database manager for CRUD operations on papers."""

from typing import Optional

from sqlalchemy.orm import Session

from ..database.models import (
    LearningScienceMetadata,
    Paper,
    StudyMetadata,
    get_db_session,
)


class DatabaseManager:
    """Context manager for database operations."""

    def __init__(self):
        self.session: Optional[Session] = None

    def __enter__(self):
        self.session = get_db_session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            if exc_type is None:
                self.session.commit()
            else:
                self.session.rollback()
            self.session.close()

    def get_all_papers(self) -> list[dict]:
        """Get all papers from database."""
        papers = self.session.query(Paper).all()
        return [self._paper_to_dict(p) for p in papers]

    def get_paper_by_id(self, paper_id: int) -> Optional[dict]:
        """Get a single paper by ID."""
        paper = self.session.query(Paper).filter_by(id=paper_id).first()
        return self._paper_to_dict(paper) if paper else None

    def add_paper(self, data: dict) -> dict:
        """Add a new paper to the database."""
        # Normalize authors to list of strings
        authors = data.get("authors", [])
        if authors:
            normalized_authors = []
            for author in authors:
                if isinstance(author, str):
                    normalized_authors.append(author)
                elif isinstance(author, dict) and "name" in author:
                    normalized_authors.append(author["name"])
                else:
                    # Fallback: try to convert to string
                    normalized_authors.append(str(author))
            authors = normalized_authors

        paper = Paper(
            title=data.get("title", ""),
            authors=authors,  # Always strings now
            year=data.get("year"),
            doi=data.get("doi"),
            s2_id=data.get("s2_id"),
            citation_count=data.get("citation_count", 0),
            pdf_path=data.get("pdf_path"),
            abstract=data.get("abstract"),
            full_text=data.get("full_text"),
        )
        self.session.add(paper)
        self.session.flush()  # Get the ID

        # Add study metadata if provided
        if data.get("study_metadata"):
            study_meta = StudyMetadata(
                paper_id=paper.id,
                methodology=data["study_metadata"].get("methodology"),
                sample_size_baseline=data["study_metadata"].get("sample_size_baseline"),
                sample_size_endline=data["study_metadata"].get("sample_size_endline"),
                effect_sizes=data["study_metadata"].get("effect_sizes"),
            )
            self.session.add(study_meta)

        # Add learning science metadata if provided
        if data.get("learning_science_metadata"):
            ls_meta = LearningScienceMetadata(
                paper_id=paper.id,
                learning_domain=data["learning_science_metadata"].get(
                    "learning_domain"
                ),
                intervention_type=data["learning_science_metadata"].get(
                    "intervention_type"
                ),
                age_group=data["learning_science_metadata"].get("age_group"),
            )
            self.session.add(ls_meta)

        self.session.flush()
        return self._paper_to_dict(paper)

    def search_papers(self, query: str) -> list[dict]:
        """Search papers by title, abstract, or authors."""
        papers = (
            self.session.query(Paper)
            .filter(
                (Paper.title.contains(query))
                | (Paper.abstract.contains(query))
                | (Paper.authors.contains(query))
            )
            .all()
        )
        return [self._paper_to_dict(p) for p in papers]

    def delete_papers(self, paper_ids: list[int]) -> int:
        """Delete multiple papers by their IDs. Returns number of deleted papers."""
        if not paper_ids:
            return 0

        papers = self.session.query(Paper).filter(Paper.id.in_(paper_ids)).all()
        count = len(papers)
        for paper in papers:
            self.session.delete(paper)
        return count

    def find_existing_paper(
        self, title: str, authors: list[str], year: Optional[int]
    ) -> Optional[dict]:
        """
        Find an existing paper by title, authors, and year.

        Args:
            title: Paper title
            authors: List of author names
            year: Publication year (optional)

        Returns:
            Paper dictionary if found, None otherwise
        """
        # Normalize authors to list of strings
        normalized_authors = []
        for author in authors:
            if isinstance(author, str):
                normalized_authors.append(author)
            elif isinstance(author, dict) and "name" in author:
                normalized_authors.append(author["name"])
            else:
                normalized_authors.append(str(author))

        # Search for papers with matching title
        query = self.session.query(Paper).filter(Paper.title == title)

        # Filter by year if provided
        if year is not None:
            query = query.filter(Paper.year == year)

        # Filter by authors (check if authors list contains any of the normalized authors)
        # This is a simplified match - we check if any author matches
        matching_papers = query.all()

        # Check if authors match (case-insensitive, partial match)
        for paper in matching_papers:
            paper_authors = paper.authors or []
            # Normalize paper authors
            paper_authors_normalized = []
            for author in paper_authors:
                if isinstance(author, str):
                    paper_authors_normalized.append(author.lower())
                elif isinstance(author, dict) and "name" in author:
                    paper_authors_normalized.append(author["name"].lower())
                else:
                    paper_authors_normalized.append(str(author).lower())

            # Check if there's any overlap in authors (at least one author matches)
            normalized_authors_lower = [a.lower() for a in normalized_authors]
            if any(
                paper_author in normalized_authors_lower
                or any(
                    paper_author in norm_author or norm_author in paper_author
                    for norm_author in normalized_authors_lower
                )
                for paper_author in paper_authors_normalized
            ):
                return self._paper_to_dict(paper)

        return None

    def update_paper(self, paper_id: int, data: dict) -> dict:
        """
        Update an existing paper with new data.

        Args:
            paper_id: ID of paper to update
            data: Dictionary with updated paper data

        Returns:
            Updated paper dictionary
        """
        paper = self.session.query(Paper).filter_by(id=paper_id).first()
        if not paper:
            raise ValueError(f"Paper with id {paper_id} not found")

        # Normalize authors
        authors = data.get("authors", [])
        if authors:
            normalized_authors = []
            for author in authors:
                if isinstance(author, str):
                    normalized_authors.append(author)
                elif isinstance(author, dict) and "name" in author:
                    normalized_authors.append(author["name"])
                else:
                    normalized_authors.append(str(author))
            authors = normalized_authors

        # Update paper fields
        if "title" in data:
            paper.title = data["title"]
        if "authors" in data:
            paper.authors = authors
        if "year" in data:
            paper.year = data.get("year")
        if "doi" in data:
            paper.doi = data.get("doi")
        if "s2_id" in data:
            paper.s2_id = data.get("s2_id")
        if "citation_count" in data:
            paper.citation_count = data.get("citation_count", 0)
        if "pdf_path" in data:
            paper.pdf_path = data.get("pdf_path")
        if "abstract" in data:
            paper.abstract = data.get("abstract")
        if "full_text" in data:
            paper.full_text = data.get("full_text")

        # Update or create study metadata
        if "study_metadata" in data:
            if paper.study_metadata:
                # Update existing
                study_meta = paper.study_metadata
                study_meta.methodology = data["study_metadata"].get("methodology")
                study_meta.sample_size_baseline = data["study_metadata"].get(
                    "sample_size_baseline"
                )
                study_meta.sample_size_endline = data["study_metadata"].get(
                    "sample_size_endline"
                )
                study_meta.effect_sizes = data["study_metadata"].get("effect_sizes")
            else:
                # Create new
                study_meta = StudyMetadata(
                    paper_id=paper.id,
                    methodology=data["study_metadata"].get("methodology"),
                    sample_size_baseline=data["study_metadata"].get(
                        "sample_size_baseline"
                    ),
                    sample_size_endline=data["study_metadata"].get(
                        "sample_size_endline"
                    ),
                    effect_sizes=data["study_metadata"].get("effect_sizes"),
                )
                self.session.add(study_meta)

        # Update or create learning science metadata
        if "learning_science_metadata" in data:
            if paper.learning_science_metadata:
                # Update existing
                ls_meta = paper.learning_science_metadata
                ls_meta.learning_domain = data["learning_science_metadata"].get(
                    "learning_domain"
                )
                ls_meta.intervention_type = data["learning_science_metadata"].get(
                    "intervention_type"
                )
                ls_meta.age_group = data["learning_science_metadata"].get("age_group")
            else:
                # Create new
                ls_meta = LearningScienceMetadata(
                    paper_id=paper.id,
                    learning_domain=data["learning_science_metadata"].get(
                        "learning_domain"
                    ),
                    intervention_type=data["learning_science_metadata"].get(
                        "intervention_type"
                    ),
                    age_group=data["learning_science_metadata"].get("age_group"),
                )
                self.session.add(ls_meta)

        self.session.flush()
        return self._paper_to_dict(paper)

    def _paper_to_dict(self, paper: Paper) -> dict:
        """Convert Paper model to dictionary."""
        # Normalize authors to list of strings (handle both old and new formats)
        authors = paper.authors or []
        if authors:
            normalized_authors = []
            for author in authors:
                if isinstance(author, str):
                    normalized_authors.append(author)
                elif isinstance(author, dict) and "name" in author:
                    normalized_authors.append(author["name"])
                else:
                    # Fallback: try to convert to string
                    normalized_authors.append(str(author))
            authors = normalized_authors

        result = {
            "id": paper.id,
            "title": paper.title,
            "authors": authors,  # Always strings now
            "year": paper.year,
            "doi": paper.doi,
            "s2_id": paper.s2_id,
            "citation_count": paper.citation_count,
            "abstract": paper.abstract,
            "pdf_path": paper.pdf_path,
            "full_text": paper.full_text,
        }

        if paper.study_metadata:
            result["study_metadata"] = {
                "methodology": paper.study_metadata.methodology,
                "sample_size_baseline": paper.study_metadata.sample_size_baseline,
                "sample_size_endline": paper.study_metadata.sample_size_endline,
                "effect_sizes": paper.study_metadata.effect_sizes,
            }

        if paper.learning_science_metadata:
            result["learning_science_metadata"] = {
                "learning_domain": paper.learning_science_metadata.learning_domain,
                "intervention_type": paper.learning_science_metadata.intervention_type,
                "age_group": paper.learning_science_metadata.age_group,
            }

        return result
