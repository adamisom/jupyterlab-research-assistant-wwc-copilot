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
        paper = Paper(
            title=data.get("title", ""),
            authors=data.get("authors", []),
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

    def _paper_to_dict(self, paper: Paper) -> dict:
        """Convert Paper model to dictionary."""
        result = {
            "id": paper.id,
            "title": paper.title,
            "authors": paper.authors,
            "year": paper.year,
            "doi": paper.doi,
            "s2_id": paper.s2_id,
            "citation_count": paper.citation_count,
            "abstract": paper.abstract,
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
