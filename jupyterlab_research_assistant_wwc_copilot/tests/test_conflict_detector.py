"""Tests for Conflict Detection Engine."""

import pytest
from jupyterlab_research_assistant_wwc_copilot.services.conflict_detector import (
    ConflictDetector,
)


class TestConflictDetector:
    """Test conflict detection functionality."""

    def test_extract_key_findings_with_keywords(self):
        """Test extraction of findings with keywords."""
        detector = ConflictDetector()
        text = "The results show a significant effect. We found that the intervention worked. The conclusion is positive."

        findings = detector.extract_key_findings(text, max_findings=5)

        assert len(findings) > 0
        assert any("significant" in f.lower() or "found" in f.lower() for f in findings)

    def test_extract_key_findings_empty_text(self):
        """Test extraction with empty text."""
        detector = ConflictDetector()
        findings = detector.extract_key_findings("", max_findings=5)
        assert findings == []

    def test_extract_key_findings_no_keywords(self):
        """Test extraction with no keywords."""
        detector = ConflictDetector()
        text = "This is a regular sentence. Another sentence here."

        findings = detector.extract_key_findings(text, max_findings=5)

        assert findings == []

    def test_extract_key_findings_respects_max(self):
        """Test that extraction respects max_findings limit."""
        detector = ConflictDetector()
        text = "Results show A. Results show B. Results show C. Results show D. Results show E. Results show F."

        findings = detector.extract_key_findings(text, max_findings=3)

        assert len(findings) <= 3

    def test_find_contradictions_without_transformers(self):
        """Test that find_contradictions returns empty list when transformers unavailable."""
        detector = ConflictDetector()
        # Force nli_pipeline to None (simulating transformers not available)
        detector.nli_pipeline = None

        contradictions = detector.find_contradictions(
            ["Finding 1"], ["Finding 2"], confidence_threshold=0.8
        )

        assert contradictions == []

    def test_find_contradictions_empty_findings(self):
        """Test find_contradictions with empty findings lists."""
        detector = ConflictDetector()
        detector.nli_pipeline = None  # Simulate transformers unavailable

        contradictions = detector.find_contradictions([], ["Finding 2"])

        assert contradictions == []

        contradictions = detector.find_contradictions(["Finding 1"], [])

        assert contradictions == []

