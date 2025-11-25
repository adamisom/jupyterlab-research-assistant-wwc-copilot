"""Tests for Forest Plot Visualizer."""

import pytest
import base64
from jupyterlab_research_assistant_wwc_copilot.services.visualizer import Visualizer


class TestVisualizer:
    """Test forest plot generation."""

    def test_create_forest_plot_returns_base64(self):
        """Test that forest plot returns a valid base64 string."""
        visualizer = Visualizer()
        studies = [
            {"effect_size": 0.5, "ci_lower": 0.2, "ci_upper": 0.8, "study_label": "Study A"},
            {"effect_size": 0.3, "ci_lower": 0.1, "ci_upper": 0.5, "study_label": "Study B"},
        ]

        image_base64 = visualizer.create_forest_plot(
            studies, pooled_effect=0.4, ci_lower=0.2, ci_upper=0.6
        )

        assert isinstance(image_base64, str)
        assert len(image_base64) > 0

        # Verify it's valid base64
        try:
            decoded = base64.b64decode(image_base64)
            assert len(decoded) > 0
            # Verify it's a PNG (starts with PNG signature)
            assert decoded[:8] == b"\x89PNG\r\n\x1a\n"
        except Exception:
            pytest.fail("Invalid base64 encoding")

    def test_create_forest_plot_with_default_study_labels(self):
        """Test forest plot with default study labels."""
        visualizer = Visualizer()
        studies = [
            {"effect_size": 0.5, "ci_lower": 0.2, "ci_upper": 0.8},
            {"effect_size": 0.3, "ci_lower": 0.1, "ci_upper": 0.5},
        ]

        image_base64 = visualizer.create_forest_plot(
            studies, pooled_effect=0.4, ci_lower=0.2, ci_upper=0.6
        )

        assert isinstance(image_base64, str)
        assert len(image_base64) > 0

    def test_create_forest_plot_with_custom_title(self):
        """Test forest plot with custom title."""
        visualizer = Visualizer()
        studies = [
            {"effect_size": 0.5, "ci_lower": 0.2, "ci_upper": 0.8, "study_label": "Study A"},
        ]

        image_base64 = visualizer.create_forest_plot(
            studies,
            pooled_effect=0.5,
            ci_lower=0.2,
            ci_upper=0.8,
            title="Custom Title",
        )

        assert isinstance(image_base64, str)
        assert len(image_base64) > 0

    def test_create_forest_plot_with_multiple_studies(self):
        """Test forest plot with multiple studies."""
        visualizer = Visualizer()
        studies = [
            {"effect_size": 0.5, "ci_lower": 0.2, "ci_upper": 0.8, "study_label": f"Study {i}"}
            for i in range(10)
        ]

        image_base64 = visualizer.create_forest_plot(
            studies, pooled_effect=0.4, ci_lower=0.2, ci_upper=0.6
        )

        assert isinstance(image_base64, str)
        assert len(image_base64) > 0

    def test_create_forest_plot_custom_figsize(self):
        """Test forest plot with custom figure size."""
        visualizer = Visualizer()
        studies = [
            {"effect_size": 0.5, "ci_lower": 0.2, "ci_upper": 0.8, "study_label": "Study A"},
        ]

        image_base64 = visualizer.create_forest_plot(
            studies, pooled_effect=0.5, ci_lower=0.2, ci_upper=0.8, figsize=(12, 10)
        )

        assert isinstance(image_base64, str)
        assert len(image_base64) > 0

    def test_create_funnel_plot_returns_base64(self):
        """Test that funnel plot returns a valid base64 string."""
        visualizer = Visualizer()
        effect_sizes = [0.5, 0.3, 0.7, 0.4, 0.6]
        std_errors = [0.15, 0.12, 0.18, 0.14, 0.16]
        labels = ["Study A", "Study B", "Study C", "Study D", "Study E"]

        image_base64 = visualizer.create_funnel_plot(effect_sizes, std_errors, labels)

        assert isinstance(image_base64, str)
        assert len(image_base64) > 0

        # Verify it's valid base64
        try:
            decoded = base64.b64decode(image_base64)
            assert len(decoded) > 0
            # Verify it's a PNG (starts with PNG signature)
            assert decoded[:8] == b"\x89PNG\r\n\x1a\n"
        except Exception:
            pytest.fail("Invalid base64 encoding")

    def test_create_funnel_plot_with_custom_title(self):
        """Test funnel plot with custom title."""
        visualizer = Visualizer()
        effect_sizes = [0.5, 0.3]
        std_errors = [0.15, 0.12]
        labels = ["Study A", "Study B"]

        image_base64 = visualizer.create_funnel_plot(
            effect_sizes, std_errors, labels, title="Custom Funnel Plot"
        )

        assert isinstance(image_base64, str)
        assert len(image_base64) > 0

    def test_create_funnel_plot_with_multiple_studies(self):
        """Test funnel plot with multiple studies."""
        visualizer = Visualizer()
        effect_sizes = [0.5 + i * 0.1 for i in range(10)]
        std_errors = [0.15 + i * 0.01 for i in range(10)]
        labels = [f"Study {i}" for i in range(10)]

        image_base64 = visualizer.create_funnel_plot(effect_sizes, std_errors, labels)

        assert isinstance(image_base64, str)
        assert len(image_base64) > 0

