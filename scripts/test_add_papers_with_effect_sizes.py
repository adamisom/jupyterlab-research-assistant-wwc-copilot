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

from jupyterlab_research_assistant_wwc_copilot.services.db_manager import (
    DatabaseManager,
)


def add_test_papers():
    """Add test papers with effect sizes for testing."""
    papers_data = [
        {
            "title": "Effectiveness of Spaced Repetition on Math Achievement",
            "authors": ["Smith, J.", "Doe, A."],
            "year": 2023,
            "abstract": (
                "This study examined the effect of spaced repetition "
                "on math achievement."
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
        },
        {
            "title": "Active Learning Strategies in Science Education",
            "authors": ["Johnson, M.", "Williams, K."],
            "year": 2022,
            "abstract": "A randomized controlled trial of active learning strategies.",
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
        },
        {
            "title": "Peer Tutoring Impact on Reading Comprehension",
            "authors": ["Brown, S.", "Davis, L.", "Miller, R."],
            "year": 2023,
            "abstract": "Quasi-experimental study of peer tutoring interventions.",
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
        },
        {
            "title": "Multimedia Learning in History Education",
            "authors": ["Wilson, T.", "Anderson, P."],
            "year": 2022,
            "abstract": (
                "Experimental study comparing multimedia vs. traditional instruction."
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
            paper = db.add_paper(paper_data)
            added_papers.append(paper)
            print(f"✓ Added: {paper['title']} (ID: {paper['id']})")  # noqa: T201

    print(f"\n✓ Successfully added {len(added_papers)} papers with effect sizes")  # noqa: T201
    print("\nYou can now test:")  # noqa: T201
    print("  - Meta-analysis (2+ papers)")  # noqa: T201
    print("  - Bias assessment (3+ papers)")  # noqa: T201
    print("  - Sensitivity analysis (3+ papers)")  # noqa: T201
    print("  - Subgroup analysis (2+ papers with subgroup metadata)")  # noqa: T201
    print("  - WWC Assessment (papers have sample sizes and attrition data)")  # noqa: T201
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
