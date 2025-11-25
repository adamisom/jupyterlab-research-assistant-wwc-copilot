"""Tests for Meta-Analysis Engine."""

from typing import Optional
import pytest
import numpy as np
from jupyterlab_research_assistant_wwc_copilot.services.meta_analyzer import MetaAnalyzer


class TestMetaAnalyzer:
    """Test meta-analysis functionality."""

    def test_requires_at_least_two_studies(self):
        """Test that meta-analysis requires at least 2 studies."""
        analyzer = MetaAnalyzer()
        studies = [{"effect_size": 0.5, "std_error": 0.15}]

        with pytest.raises(ValueError, match="at least 2 studies"):
            analyzer.perform_random_effects_meta_analysis(studies)

    def test_requires_positive_standard_errors(self):
        """Test that standard errors must be positive."""
        analyzer = MetaAnalyzer()
        studies = [
            {"effect_size": 0.5, "std_error": 0.15},
            {"effect_size": 0.3, "std_error": 0.0},  # Invalid
        ]

        with pytest.raises(ValueError, match="Standard errors must be positive"):
            analyzer.perform_random_effects_meta_analysis(studies)

    def test_basic_meta_analysis(self):
        """Test basic meta-analysis with two studies."""
        analyzer = MetaAnalyzer()
        studies = [
            {"effect_size": 0.5, "std_error": 0.15, "study_label": "Study A", "paper_id": 1},
            {"effect_size": 0.3, "std_error": 0.12, "study_label": "Study B", "paper_id": 2},
        ]

        result = analyzer.perform_random_effects_meta_analysis(studies)

        assert "pooled_effect" in result
        assert "ci_lower" in result
        assert "ci_upper" in result
        assert "p_value" in result
        assert "tau_squared" in result
        assert "i_squared" in result
        assert "q_statistic" in result
        assert "q_p_value" in result
        assert "n_studies" in result
        assert "studies" in result

        assert result["n_studies"] == 2
        assert len(result["studies"]) == 2
        assert result["ci_lower"] < result["pooled_effect"] < result["ci_upper"]

    def test_meta_analysis_with_multiple_studies(self):
        """Test meta-analysis with multiple studies."""
        analyzer = MetaAnalyzer()
        studies = [
            {"effect_size": 0.5, "std_error": 0.15, "study_label": "Study A", "paper_id": 1},
            {"effect_size": 0.3, "std_error": 0.12, "study_label": "Study B", "paper_id": 2},
            {"effect_size": 0.7, "std_error": 0.18, "study_label": "Study C", "paper_id": 3},
            {"effect_size": 0.4, "std_error": 0.14, "study_label": "Study D", "paper_id": 4},
        ]

        result = analyzer.perform_random_effects_meta_analysis(studies)

        assert result["n_studies"] == 4
        assert len(result["studies"]) == 4
        assert isinstance(result["pooled_effect"], float)
        assert isinstance(result["i_squared"], float)
        assert 0 <= result["i_squared"] <= 100

    def test_study_results_include_weights(self):
        """Test that individual study results include weights."""
        analyzer = MetaAnalyzer()
        studies = [
            {"effect_size": 0.5, "std_error": 0.15, "study_label": "Study A"},
            {"effect_size": 0.3, "std_error": 0.12, "study_label": "Study B"},
        ]

        result = analyzer.perform_random_effects_meta_analysis(studies)

        for study in result["studies"]:
            assert "weight" in study
            assert "effect_size" in study
            assert "std_error" in study
            assert "ci_lower" in study
            assert "ci_upper" in study
            assert 0 <= study["weight"] <= 1

        # Weights should sum to approximately 1
        total_weight = sum(s["weight"] for s in result["studies"])
        assert abs(total_weight - 1.0) < 0.001

    def test_study_results_include_confidence_intervals(self):
        """Test that study results include confidence intervals."""
        analyzer = MetaAnalyzer()
        studies = [
            {"effect_size": 0.5, "std_error": 0.15, "study_label": "Study A"},
            {"effect_size": 0.3, "std_error": 0.12, "study_label": "Study B"},
        ]

        result = analyzer.perform_random_effects_meta_analysis(studies)

        for study in result["studies"]:
            assert study["ci_lower"] < study["effect_size"] < study["ci_upper"]

    def test_default_study_labels(self):
        """Test that studies without labels get default labels."""
        analyzer = MetaAnalyzer()
        studies = [
            {"effect_size": 0.5, "std_error": 0.15},
            {"effect_size": 0.3, "std_error": 0.12},
        ]

        result = analyzer.perform_random_effects_meta_analysis(studies)

        assert result["studies"][0]["study_label"] == "Study 1"
        assert result["studies"][1]["study_label"] == "Study 2"

    def test_interpret_heterogeneity_low(self):
        """Test heterogeneity interpretation for low I²."""
        analyzer = MetaAnalyzer()
        assert "Low" in analyzer.interpret_heterogeneity(10.0)
        assert "Low" in analyzer.interpret_heterogeneity(24.0)

    def test_interpret_heterogeneity_moderate(self):
        """Test heterogeneity interpretation for moderate I²."""
        analyzer = MetaAnalyzer()
        assert "Moderate" in analyzer.interpret_heterogeneity(25.0)
        assert "Moderate" in analyzer.interpret_heterogeneity(49.0)

    def test_interpret_heterogeneity_substantial(self):
        """Test heterogeneity interpretation for substantial I²."""
        analyzer = MetaAnalyzer()
        assert "Substantial" in analyzer.interpret_heterogeneity(50.0)
        assert "Substantial" in analyzer.interpret_heterogeneity(74.0)

    def test_interpret_heterogeneity_considerable(self):
        """Test heterogeneity interpretation for considerable I²."""
        analyzer = MetaAnalyzer()
        assert "Considerable" in analyzer.interpret_heterogeneity(75.0)
        assert "Considerable" in analyzer.interpret_heterogeneity(90.0)

    def test_subgroup_analysis_requires_at_least_two_studies(self):
        """Test that subgroup analysis requires at least 2 studies."""
        analyzer = MetaAnalyzer()
        studies = [{"effect_size": 0.5, "std_error": 0.15, "age_group": "young"}]

        with pytest.raises(ValueError, match="at least 2 studies"):
            analyzer.perform_subgroup_meta_analysis(studies, "age_group")

    def test_subgroup_analysis_basic(self):
        """Test basic subgroup analysis."""
        analyzer = MetaAnalyzer()
        studies = [
            {"effect_size": 0.5, "std_error": 0.15, "study_label": "Study A", "age_group": "young"},
            {"effect_size": 0.3, "std_error": 0.12, "study_label": "Study B", "age_group": "young"},
            {"effect_size": 0.7, "std_error": 0.18, "study_label": "Study C", "age_group": "old"},
            {"effect_size": 0.4, "std_error": 0.14, "study_label": "Study D", "age_group": "old"},
        ]

        result = analyzer.perform_subgroup_meta_analysis(studies, "age_group")

        assert "subgroups" in result
        assert "overall" in result
        assert "subgroup_variable" in result
        assert "n_subgroups" in result
        assert "subgroup_comparison" in result
        assert result["subgroup_variable"] == "age_group"
        assert result["n_subgroups"] == 2
        assert "young" in result["subgroups"]
        assert "old" in result["subgroups"]
        assert result["overall"]["n_studies"] == 4
        
        # Check subgroup comparison structure
        comparison = result["subgroup_comparison"]
        assert "q_between" in comparison
        assert "df" in comparison
        assert "p_value" in comparison
        assert "interpretation" in comparison
        assert comparison["df"] == 1  # 2 subgroups - 1
        assert comparison["q_between"] is not None
        assert 0 <= comparison["p_value"] <= 1

    def test_subgroup_comparison_single_subgroup(self):
        """Test subgroup comparison with only one subgroup."""
        analyzer = MetaAnalyzer()
        studies = [
            {"effect_size": 0.5, "std_error": 0.15, "age_group": "young"},
            {"effect_size": 0.3, "std_error": 0.12, "age_group": "young"},
        ]

        result = analyzer.perform_subgroup_meta_analysis(studies, "age_group")

        comparison = result["subgroup_comparison"]
        assert comparison["q_between"] is None
        assert "At least 2 subgroups" in comparison["interpretation"]

    def test_subgroup_analysis_with_unknown_subgroup(self):
        """Test subgroup analysis with unknown subgroup values."""
        analyzer = MetaAnalyzer()
        studies = [
            {"effect_size": 0.5, "std_error": 0.15, "age_group": "young"},
            {"effect_size": 0.3, "std_error": 0.12, "age_group": "young"},  # Same subgroup
            {"effect_size": 0.7, "std_error": 0.18},  # Missing subgroup (will be "unknown")
            {"effect_size": 0.4, "std_error": 0.14},  # Missing subgroup (will be "unknown")
        ]

        result = analyzer.perform_subgroup_meta_analysis(studies, "age_group")

        # Should have at least one subgroup (young should work since it has 2 studies)
        assert len(result["subgroups"]) >= 1
        assert "young" in result["subgroups"]
        # Overall should include all studies
        assert result["overall"]["n_studies"] == 4

    def test_eggers_test_requires_at_least_three_studies(self):
        """Test that Egger's test requires at least 3 studies."""
        analyzer = MetaAnalyzer()
        effect_sizes = np.array([0.5, 0.3])
        std_errors = np.array([0.15, 0.12])

        result = analyzer.perform_eggers_test(effect_sizes, std_errors)
        assert result["intercept"] is None
        assert "at least 3 studies" in result["interpretation"]

    def test_eggers_test_basic(self):
        """Test basic Egger's test."""
        analyzer = MetaAnalyzer()
        effect_sizes = np.array([0.5, 0.3, 0.7, 0.4, 0.6])
        std_errors = np.array([0.15, 0.12, 0.18, 0.14, 0.16])

        result = analyzer.perform_eggers_test(effect_sizes, std_errors)

        assert "intercept" in result
        assert "intercept_se" in result
        assert "intercept_pvalue" in result
        assert "interpretation" in result
        assert result["intercept"] is not None
        assert result["intercept_se"] is not None
        assert result["intercept_pvalue"] is not None
        assert 0 <= result["intercept_pvalue"] <= 1

    def test_sensitivity_analysis_requires_at_least_three_studies(self):
        """Test that sensitivity analysis requires at least 3 studies."""
        analyzer = MetaAnalyzer()
        studies = [
            {"effect_size": 0.5, "std_error": 0.15},
            {"effect_size": 0.3, "std_error": 0.12},
        ]

        with pytest.raises(ValueError, match="at least 3 studies"):
            analyzer.perform_sensitivity_analysis(studies)

    def test_sensitivity_analysis_basic(self):
        """Test basic sensitivity analysis."""
        import warnings
        
        analyzer = MetaAnalyzer()
        studies = [
            {"effect_size": 0.5, "std_error": 0.15, "study_label": "Study A", "paper_id": 1},
            {"effect_size": 0.3, "std_error": 0.12, "study_label": "Study B", "paper_id": 2},
            {"effect_size": 0.7, "std_error": 0.18, "study_label": "Study C", "paper_id": 3},
            {"effect_size": 0.4, "std_error": 0.14, "study_label": "Study D", "paper_id": 4},
        ]

        # Suppress expected warnings from statsmodels for edge cases
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=RuntimeWarning, module="statsmodels")
            result = analyzer.perform_sensitivity_analysis(studies)

        assert "overall_effect" in result
        assert "leave_one_out" in result
        assert "influence_diagnostics" in result
        assert "n_studies" in result
        assert result["n_studies"] == 4
        assert len(result["leave_one_out"]) == 4
        assert len(result["influence_diagnostics"]) == 4

        # Check leave-one-out structure
        for loo in result["leave_one_out"]:
            assert "removed_study" in loo
            assert "pooled_effect" in loo
            assert "ci_lower" in loo
            assert "ci_upper" in loo
            assert "difference_from_overall" in loo

        # Check influence diagnostics structure
        for diag in result["influence_diagnostics"]:
            assert "study_label" in diag
            assert "influence_score" in diag
            assert "weight" in diag
            assert "effect_size" in diag
            assert diag["influence_score"] >= 0
            assert 0 <= diag["weight"] <= 1

    def test_sensitivity_analysis_influence_sorted(self):
        """Test that influence diagnostics are sorted by influence score."""
        analyzer = MetaAnalyzer()
        studies = [
            {"effect_size": 0.5, "std_error": 0.15, "study_label": "Study A"},
            {"effect_size": 0.3, "std_error": 0.12, "study_label": "Study B"},
            {"effect_size": 0.7, "std_error": 0.18, "study_label": "Study C"},
        ]

        result = analyzer.perform_sensitivity_analysis(studies)

        influence_scores = [d["influence_score"] for d in result["influence_diagnostics"]]
        assert influence_scores == sorted(influence_scores, reverse=True)

