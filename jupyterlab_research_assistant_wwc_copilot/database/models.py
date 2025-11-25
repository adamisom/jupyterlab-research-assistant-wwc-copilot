"""SQLAlchemy models for the research library database."""

from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from pathlib import Path

Base = declarative_base()


class Paper(Base):
    """Model representing an academic paper."""

    __tablename__ = "papers"

    id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=False)
    authors = Column(JSON)  # List of author names
    year = Column(Integer)
    doi = Column(String(255))
    s2_id = Column(String(255))  # Semantic Scholar ID
    citation_count = Column(Integer, default=0)
    pdf_path = Column(Text)  # Filesystem path to PDF
    abstract = Column(Text)
    full_text = Column(Text)  # Extracted PDF text

    # Relationships
    study_metadata = relationship(
        "StudyMetadata",
        back_populates="paper",
        uselist=False,
        cascade="all, delete-orphan"
    )
    learning_science_metadata = relationship(
        "LearningScienceMetadata",
        back_populates="paper",
        uselist=False,
        cascade="all, delete-orphan"
    )


class StudyMetadata(Base):
    """Model representing study metadata for a paper."""

    __tablename__ = "study_metadata"

    paper_id = Column(Integer, ForeignKey("papers.id"), primary_key=True)
    methodology = Column(String(50))  # e.g., "RCT", "Quasi-experimental"
    sample_size_baseline = Column(Integer)
    sample_size_endline = Column(Integer)
    effect_sizes = Column(JSON)  # {"outcome_name": {"d": 0.5, "se": 0.1}, ...}

    paper = relationship("Paper", back_populates="study_metadata")


class LearningScienceMetadata(Base):
    """Model representing learning science-specific metadata."""

    __tablename__ = "learning_science_metadata"

    paper_id = Column(Integer, ForeignKey("papers.id"), primary_key=True)
    learning_domain = Column(String(50))  # e.g., "cognitive", "affective"
    intervention_type = Column(String(100))
    age_group = Column(String(50))  # e.g., "young", "old", "mixed"

    paper = relationship("Paper", back_populates="learning_science_metadata")


def get_db_path() -> Path:
    """Get the database file path in JupyterLab's data directory."""
    # Use JupyterLab's application data directory
    data_dir = Path.home() / ".jupyter" / "research_assistant"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "research_library.db"


def create_db_engine():
    """Create SQLAlchemy engine with database file."""
    db_path = get_db_path()
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(engine)
    return engine


def get_db_session():
    """Get a database session."""
    engine = create_db_engine()
    Session = sessionmaker(bind=engine)
    return Session()

