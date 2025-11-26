"""
Script to add test papers with effect sizes for testing meta-analysis features.

This script adds papers with effect size data to the library, which is required
for testing:
- Meta-analysis
- Bias assessment (requires 3+ papers)
- Sensitivity analysis (requires 3+ papers)
- Subgroup analysis (requires effect sizes + subgroup metadata)

Usage:
    python scripts/test_add_papers_with_effect_sizes.py

Or run in a Jupyter notebook cell.
"""

import sys
from pathlib import Path

# Add parent directory to path to import the extension
sys.path.insert(0, str(Path(__file__).parent.parent))

import fitz  # PyMuPDF

from jupyterlab_research_assistant_wwc_copilot.services.db_manager import (
    DatabaseManager,
)


def create_simple_pdf(
    title: str, authors: list[str], abstract: str, content: str, upload_dir: Path
) -> Path:
    """Create a simple PDF file with the given content."""
    doc = fitz.open()  # Create new PDF
    page = doc.new_page()

    # Add title
    title_rect = fitz.Rect(50, 50, 550, 100)
    page.insert_text(
        title_rect.tl, title, fontsize=16, fontname="helv", color=(0, 0, 0)
    )

    # Add authors
    authors_text = ", ".join(authors)
    authors_rect = fitz.Rect(50, 110, 550, 140)
    page.insert_text(
        authors_rect.tl, authors_text, fontsize=12, fontname="helv", color=(0, 0, 0)
    )

    # Add abstract
    abstract_rect = fitz.Rect(50, 160, 550, 300)
    page.insert_text(
        abstract_rect.tl,
        f"Abstract\n\n{abstract}",
        fontsize=10,
        fontname="helv",
        color=(0, 0, 0),
    )

    # Add content
    content_rect = fitz.Rect(50, 320, 550, 750)
    page.insert_text(
        content_rect.tl, content, fontsize=10, fontname="helv", color=(0, 0, 0)
    )

    # Save PDF
    safe_filename = (
        "".join(c for c in title if c.isalnum() or c in (" ", "-", "_")).rstrip()
        + ".pdf"
    )
    safe_filename = safe_filename.replace(" ", "_")
    pdf_path = upload_dir / safe_filename
    doc.save(str(pdf_path))
    doc.close()

    return pdf_path


def add_test_papers():
    """
    Add test papers with effect sizes for testing.

    NOTE: This script bypasses several high-level API/service layer features:
    - Duplicate detection: Calls db.add_paper() directly, bypassing LibraryHandler
      and ImportService duplicate checks. Papers will be added even if duplicates exist.
    - PDF upload workflow: Creates PDFs directly and adds them to paper_data,
      bypassing ImportService.import_pdf() which handles file validation, AI extraction,
      and duplicate detection for PDF uploads.
    - AI extraction pipeline: Does not trigger AI metadata extraction that would
      normally run during PDF import.
    - API response formatting: Does not use the API response format with is_duplicate
      flags that the frontend expects.

    This is intentional for testing purposes - the script needs to populate the database
    directly without going through the full API/service workflows.
    """
    # Set up upload directory
    upload_dir = Path.home() / ".jupyter" / "research_assistant" / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)

    papers_data = [
        {
            "title": "Effectiveness of Spaced Repetition on Math Achievement",
            "authors": ["Smith, J.", "Doe, A."],
            "year": 2023,
            "abstract": (
                "This study examined the effect of spaced repetition on math achievement. "
                "Results show a significant improvement in test scores for students using "
                "spaced repetition compared to traditional study methods. The findings "
                "demonstrate that spaced repetition leads to better retention of mathematical "
                "concepts. Evidence suggests this intervention is effective for elementary "
                "school students."
            ),
            "study_metadata": {
                "methodology": "RCT",
                "sample_size_baseline": 100,
                "sample_size_endline": 95,
                "treatment_attrition": 0.04,  # 4% attrition in treatment
                "control_attrition": 0.06,  # 6% attrition in control
                "effect_sizes": {
                    "math_achievement": {"d": 0.45, "se": 0.12},
                    "retention": {"d": 0.38, "se": 0.14},
                },
            },
            "learning_science_metadata": {
                "learning_domain": "mathematics",
                "intervention_type": "spaced_repetition",
                "age_group": "elementary",
            },
            # This paper will have a full PDF
            "_create_pdf": True,
            "_pdf_content": (
                "Introduction\n\n"
                "This randomized controlled trial examined the effectiveness of spaced repetition "
                "on math achievement in elementary school students. Spaced repetition is a learning "
                "technique that involves reviewing material at increasing intervals over time.\n\n"
                "Methods\n\n"
                "We randomly assigned 100 students to either a spaced repetition condition or a "
                "traditional study condition. Students in the spaced repetition group reviewed math "
                "concepts at increasing intervals, while the control group used traditional study methods.\n\n"
                "Results\n\n"
                "Results show a significant improvement in test scores for students using spaced "
                "repetition (d = 0.45, SE = 0.12). The findings demonstrate that spaced repetition "
                "leads to better retention of mathematical concepts (d = 0.38, SE = 0.14).\n\n"
                "Conclusion\n\n"
                "Evidence suggests this intervention is effective for elementary school students. "
                "Spaced repetition shows promise as an effective learning strategy for mathematics."
            ),
        },
        {
            "title": "Active Learning Strategies in Science Education",
            "authors": ["Johnson, M.", "Williams, K."],
            "year": 2022,
            "abstract": (
                "A randomized controlled trial of active learning strategies in science education. "
                "The results show that students in the active learning group showed significant "
                "improvements in science achievement. We found that hands-on experiments and "
                "collaborative activities had a positive impact on learning outcomes. The "
                "conclusion indicates that active learning is more effective than traditional "
                "lecture-based instruction for middle school students."
            ),
            "study_metadata": {
                "methodology": "RCT",
                "sample_size_baseline": 150,
                "sample_size_endline": 145,
                "treatment_attrition": 0.03,  # 3% attrition in treatment
                "control_attrition": 0.03,  # 3% attrition in control
                "effect_sizes": {
                    "science_achievement": {"d": 0.62, "se": 0.15},
                    "engagement": {"d": 0.51, "se": 0.13},
                },
            },
            "learning_science_metadata": {
                "learning_domain": "science",
                "intervention_type": "active_learning",
                "age_group": "middle_school",
            },
            # This paper will have a full PDF
            "_create_pdf": True,
            "_pdf_content": (
                "Introduction\n\n"
                "This randomized controlled trial examined the effectiveness of active learning "
                "strategies in science education for middle school students. Active learning "
                "involves hands-on experiments, collaborative activities, and student-centered "
                "instruction.\n\n"
                "Methods\n\n"
                "We randomly assigned 150 students to either an active learning condition or a "
                "traditional lecture-based condition. The active learning group engaged in hands-on "
                "experiments and collaborative activities, while the control group received "
                "traditional lecture-based instruction.\n\n"
                "Results\n\n"
                "The results show that students in the active learning group showed significant "
                "improvements in science achievement (d = 0.62, SE = 0.15). We found that "
                "hands-on experiments and collaborative activities had a positive impact on "
                "learning outcomes (d = 0.51, SE = 0.13).\n\n"
                "Conclusion\n\n"
                "The conclusion indicates that active learning is more effective than traditional "
                "lecture-based instruction for middle school students."
            ),
        },
        {
            "title": "Peer Tutoring Impact on Reading Comprehension",
            "authors": ["Brown, S.", "Davis, L.", "Miller, R."],
            "year": 2023,
            "abstract": (
                "Quasi-experimental study of peer tutoring interventions in reading "
                "comprehension. The study revealed that peer tutoring significantly "
                "improved reading scores. Findings indicate that students who participated "
                "in peer tutoring showed greater gains than those in the control group. "
                "Evidence suggests peer tutoring is an effective strategy for improving "
                "reading comprehension in elementary students."
            ),
            "study_metadata": {
                "methodology": "Quasi-experimental",
                "sample_size_baseline": 200,
                "sample_size_endline": 195,
                "treatment_attrition": 0.02,  # 2% attrition in treatment
                "control_attrition": 0.03,  # 3% attrition in control
                "baseline_means": {"treatment": 50.2, "control": 50.0},
                "baseline_sds": {"treatment": 10.5, "control": 10.3},
                "effect_sizes": {
                    "reading_comprehension": {"d": 0.38, "se": 0.11},
                    "vocabulary": {"d": 0.29, "se": 0.12},
                },
            },
            "learning_science_metadata": {
                "learning_domain": "reading",
                "intervention_type": "peer_tutoring",
                "age_group": "elementary",
            },
            # This paper will have a full PDF
            "_create_pdf": True,
            "_pdf_content": (
                "Introduction\n\n"
                "This quasi-experimental study examined the impact of peer tutoring interventions "
                "on reading comprehension in elementary school students. Peer tutoring involves "
                "students teaching and learning from each other in structured pairs or small groups.\n\n"
                "Methods\n\n"
                "We assigned 200 students to either a peer tutoring condition or a control condition. "
                "Students in the peer tutoring group worked in pairs to practice reading comprehension "
                "strategies, while the control group received traditional reading instruction.\n\n"
                "Results\n\n"
                "The study revealed that peer tutoring significantly improved reading scores "
                "(d = 0.38, SE = 0.11). Findings indicate that students who participated in peer "
                "tutoring showed greater gains than those in the control group. Vocabulary scores "
                "also improved (d = 0.29, SE = 0.12).\n\n"
                "Conclusion\n\n"
                "Evidence suggests peer tutoring is an effective strategy for improving reading "
                "comprehension in elementary students."
            ),
        },
        {
            "title": "Multimedia Learning in History Education",
            "authors": ["Wilson, T.", "Anderson, P."],
            "year": 2022,
            "abstract": (
                "Experimental study comparing multimedia vs. traditional instruction in history "
                "education. Results demonstrate that multimedia instruction led to significantly "
                "higher test scores. The findings show that students learned more effectively "
                "when using interactive multimedia content. Evidence indicates that multimedia "
                "approaches have a positive impact on history knowledge retention for high school "
                "students."
            ),
            "study_metadata": {
                "methodology": "RCT",
                "sample_size_baseline": 120,
                "sample_size_endline": 118,
                "treatment_attrition": 0.015,  # 1.5% attrition in treatment
                "control_attrition": 0.017,  # 1.7% attrition in control
                "effect_sizes": {
                    "history_knowledge": {"d": 0.55, "se": 0.14},
                },
            },
            "learning_science_metadata": {
                "learning_domain": "social_studies",
                "intervention_type": "multimedia",
                "age_group": "high_school",
            },
        },
        {
            "title": "Feedback Timing Effects on Writing Quality",
            "authors": ["Garcia, M.", "Lee, J."],
            "year": 2023,
            "abstract": "Randomized trial examining immediate vs. delayed feedback.",
            "study_metadata": {
                "methodology": "RCT",
                "sample_size_baseline": 180,
                "sample_size_endline": 175,
                "treatment_attrition": 0.025,  # 2.5% attrition in treatment
                "control_attrition": 0.028,  # 2.8% attrition in control
                "effect_sizes": {
                    "writing_quality": {"d": 0.41, "se": 0.13},
                    "revision_quality": {"d": 0.33, "se": 0.12},
                },
            },
            "learning_science_metadata": {
                "learning_domain": "writing",
                "intervention_type": "feedback",
                "age_group": "middle_school",
            },
        },
    ]

    added_papers = []
    with DatabaseManager() as db:
        for paper_data in papers_data:
            # Check if we need to create a PDF for this paper
            create_pdf = paper_data.pop("_create_pdf", False)
            pdf_content = paper_data.pop("_pdf_content", None)

            if create_pdf and pdf_content:
                # Create PDF file
                pdf_path = create_simple_pdf(
                    title=paper_data["title"],
                    authors=paper_data["authors"],
                    abstract=paper_data["abstract"],
                    content=pdf_content,
                    upload_dir=upload_dir,
                )
                # Read the PDF content to get full_text
                doc = fitz.open(str(pdf_path))
                full_text = ""
                for page in doc:
                    full_text += page.get_text() + "\n"
                doc.close()

                # Add PDF data to paper
                paper_data["pdf_path"] = str(pdf_path)
                paper_data["full_text"] = full_text
                print(f"✓ Created PDF: {pdf_path.name}")  # noqa: T201

            paper = db.add_paper(paper_data)
            added_papers.append(paper)
            pdf_status = (
                "📄 Full PDF" if paper_data.get("pdf_path") else "📋 Metadata Only"
            )
            print(f"✓ Added: {paper['title']} (ID: {paper['id']}) - {pdf_status}")  # noqa: T201

    print(f"\n✓ Successfully added {len(added_papers)} papers with effect sizes")  # noqa: T201
    print("\nPapers with Full PDFs (3):")  # noqa: T201
    print("  1. Effectiveness of Spaced Repetition on Math Achievement")  # noqa: T201
    print("  2. Active Learning Strategies in Science Education")  # noqa: T201
    print("  3. Peer Tutoring Impact on Reading Comprehension")  # noqa: T201
    print("\nPapers with Metadata Only (2):")  # noqa: T201
    print("  4. Multimedia Learning in History Education")  # noqa: T201
    print("  5. Feedback Timing Effects on Writing Quality")  # noqa: T201
    print("\nYou can now test:")  # noqa: T201
    print("  - Meta-analysis (2+ papers with full PDFs)")  # noqa: T201
    print("  - Bias assessment (3+ papers with full PDFs)")  # noqa: T201
    print("  - Sensitivity analysis (3+ papers with full PDFs)")  # noqa: T201
    print("  - Subgroup analysis (2+ papers with subgroup metadata)")  # noqa: T201
    print("  - WWC Assessment (papers have sample sizes and attrition data)")  # noqa: T201
    print("  - Duplicate detection (try uploading PDFs for papers 1-3)")  # noqa: T201
    print("  - Synthesis button logic (select 2+ full-PDF papers, button appears)")  # noqa: T201
    print("  - Synthesis button logic (select metadata-only papers, button disappears)")  # noqa: T201
    print("\nNote: For WWC assessment to pass, you need to:")  # noqa: T201
    print("  1. Set 'Randomization Documented' = true")  # noqa: T201
    print("  2. Choose an attrition boundary (cautious or optimistic)")  # noqa: T201
    print(  # noqa: T201
        "  - Papers 1-5 have low attrition rates that should pass with "
        "'optimistic' boundary"
    )

    return added_papers


if __name__ == "__main__":
    add_test_papers()
