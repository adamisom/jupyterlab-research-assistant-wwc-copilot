"""Tests for Meta-Analysis Engine."""

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

