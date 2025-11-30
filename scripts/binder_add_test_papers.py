"""
Quick script to add test papers with effect sizes on Binder.
Run this in a Jupyter notebook cell or Python script.

Usage in Jupyter notebook:
    %run scripts/binder_add_test_papers.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from jupyterlab_research_assistant_wwc_copilot.services.db_manager import (
    DatabaseManager,
)

# Test papers data with effect sizes
papers_data = [
    {
        "title": "Effectiveness of Spaced Repetition on Math Achievement",
        "authors": ["Smith, J.", "Doe, A."],
        "year": 2023,
        "abstract": (
            "This study examined the effect of spaced repetition on math achievement. "
            "Results show a significant improvement in test scores for students using "
            "spaced repetition compared to traditional study methods."
        ),
        "study_metadata": {
            "methodology": "RCT",
            "sample_size_baseline": 100,
            "sample_size_endline": 95,
            "treatment_attrition": 0.04,
            "control_attrition": 0.06,
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
    },
    {
        "title": "Active Learning Strategies in Science Education",
        "authors": ["Johnson, M.", "Williams, K."],
        "year": 2022,
        "abstract": (
            "A randomized controlled trial of active learning strategies in science education. "
            "The results show that students in the active learning group showed significant "
            "improvements in science achievement."
        ),
        "study_metadata": {
            "methodology": "RCT",
            "sample_size_baseline": 150,
            "sample_size_endline": 145,
            "treatment_attrition": 0.03,
            "control_attrition": 0.03,
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
    },
    {
        "title": "Peer Tutoring Impact on Reading Comprehension",
        "authors": ["Brown, S.", "Davis, L.", "Miller, R."],
        "year": 2023,
        "abstract": (
            "Quasi-experimental study of peer tutoring interventions in reading "
            "comprehension. The study revealed that peer tutoring significantly "
            "improved reading scores."
        ),
        "study_metadata": {
            "methodology": "Quasi-experimental",
            "sample_size_baseline": 200,
            "sample_size_endline": 195,
            "treatment_attrition": 0.02,
            "control_attrition": 0.03,
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
    },
]

# Add papers to database
added_papers = []
with DatabaseManager() as db:
    for paper_data in papers_data:
        paper = db.add_paper(paper_data)
        added_papers.append(paper)
        print(f"✓ Added: {paper['title']} (ID: {paper['id']})")  # noqa: T201

print(f"\n✓ Successfully added {len(added_papers)} papers with effect sizes")  # noqa: T201
print("\nYou can now run meta-analysis on these papers!")  # noqa: T201
