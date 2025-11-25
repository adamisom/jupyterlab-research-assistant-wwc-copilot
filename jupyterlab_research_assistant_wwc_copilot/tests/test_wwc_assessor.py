"""Tests for WWC Quality Assessment Engine."""

from jupyterlab_research_assistant_wwc_copilot.services.wwc_assessor import (
    AttritionBoundary,
    WWCQualityAssessor,
    WWCRating,
)


class TestAttritionBoundaries:
    """Test attrition boundary calculations."""

    def test_low_attrition_cautious_boundary(self):
        """Test low attrition with cautious boundary."""
        assessor = WWCQualityAssessor()
        result = assessor.is_low_attrition(
            overall=0.08, differential=0.04, boundary=AttritionBoundary.CAUTIOUS
        )
        assert result is True

    def test_high_attrition_cautious_boundary(self):
        """Test high attrition with cautious boundary."""
        assessor = WWCQualityAssessor()
        result = assessor.is_low_attrition(
            overall=0.15, differential=0.06, boundary=AttritionBoundary.CAUTIOUS
        )
        assert result is False

    def test_low_attrition_optimistic_boundary(self):
        """Test low attrition with optimistic boundary."""
        assessor = WWCQualityAssessor()
        result = assessor.is_low_attrition(
            overall=0.12, differential=0.04, boundary=AttritionBoundary.OPTIMISTIC
        )
        assert result is True

    def test_high_attrition_optimistic_boundary(self):
        """Test high attrition with optimistic boundary."""
        assessor = WWCQualityAssessor()
        result = assessor.is_low_attrition(
            overall=0.15, differential=0.08, boundary=AttritionBoundary.OPTIMISTIC
        )
        assert result is False

    def test_very_high_attrition(self):
        """Test that >40% overall attrition always fails."""
        assessor = WWCQualityAssessor()
        result = assessor.is_low_attrition(
            overall=0.45, differential=0.01, boundary=AttritionBoundary.CAUTIOUS
        )
        assert result is False

    def test_none_values(self):
        """Test that None values return False."""
        assessor = WWCQualityAssessor()
        result = assessor.is_low_attrition(
            overall=None, differential=0.05, boundary=AttritionBoundary.CAUTIOUS
        )
        assert result is False

        result = assessor.is_low_attrition(
            overall=0.10, differential=None, boundary=AttritionBoundary.CAUTIOUS
        )
        assert result is False


class TestBaselineEquivalence:
    """Test baseline equivalence calculations."""

    def test_equivalent_baseline(self):
        """Test equivalent baseline groups."""
        assessor = WWCQualityAssessor()
        result = assessor.calculate_baseline_equivalence(
            treatment_mean=50.0, control_mean=50.5, treatment_sd=10.0, control_sd=10.0
        )
        assert result["status"] == "equivalent"
        assert abs(result["effect_size"]) <= 0.05

    def test_adjustable_baseline(self):
        """Test baseline requiring adjustment."""
        assessor = WWCQualityAssessor()
        # Use a difference that gives Cohen's d between 0.05 and 0.25
        # For SD=10, d=0.15 means difference of 1.5, so use 51.5
        result = assessor.calculate_baseline_equivalence(
            treatment_mean=50.0, control_mean=51.5, treatment_sd=10.0, control_sd=10.0
        )
        assert result["status"] == "adjustable"
        assert 0.05 < abs(result["effect_size"]) <= 0.25

    def test_not_equivalent_baseline(self):
        """Test non-equivalent baseline groups."""
        assessor = WWCQualityAssessor()
        result = assessor.calculate_baseline_equivalence(
            treatment_mean=50.0, control_mean=60.0, treatment_sd=10.0, control_sd=10.0
        )
        assert result["status"] == "not_equivalent"
        assert abs(result["effect_size"]) > 0.25

    def test_zero_variance(self):
        """Test baseline with zero variance."""
        assessor = WWCQualityAssessor()
        result = assessor.calculate_baseline_equivalence(
            treatment_mean=50.0, control_mean=50.0, treatment_sd=0.0, control_sd=0.0
        )
        assert result["status"] == "equivalent"
        assert result["effect_size"] == 0.0


class TestWWCAssessment:
    """Test complete WWC assessment."""

    def test_low_attrition_rct_meets_without_reservations(self):
        """Test low-attrition RCT that meets without reservations."""
        assessor = WWCQualityAssessor()
        extracted_data = {
            "baseline_n": 100,
            "endline_n": 95,
            "treatment_attrition": 0.04,
            "control_attrition": 0.06,
            "methodology": "RCT",
            "randomization_documented": True,
        }
        user_judgments = {"chosen_attrition_boundary": "cautious"}

        assessment = assessor.assess(extracted_data, user_judgments)

        assert assessment.final_rating == WWCRating.MEETS_WITHOUT_RESERVATIONS
        assert assessment.is_high_attrition is False
        assert len(assessment.rating_justification) > 0

    def test_high_attrition_with_baseline_equivalence_meets_with_reservations(self):
        """Test high-attrition RCT with baseline equivalence that meets with reservations."""
        assessor = WWCQualityAssessor()
        extracted_data = {
            "baseline_n": 100,
            "endline_n": 70,
            "treatment_attrition": 0.20,
            "control_attrition": 0.30,
            "methodology": "RCT",
            "randomization_documented": True,
            "baseline_means": {"treatment": 50.0, "control": 51.0},
            "baseline_sds": {"treatment": 10.0, "control": 10.0},
        }
        user_judgments = {
            "chosen_attrition_boundary": "cautious",
            "adjustment_strategy_is_valid": True,
        }

        assessment = assessor.assess(extracted_data, user_judgments)

        assert assessment.final_rating == WWCRating.MEETS_WITH_RESERVATIONS
        assert assessment.is_high_attrition is True
        assert assessment.baseline_equivalence_satisfied is True

    def test_no_randomization_documentation_does_not_meet(self):
        """Test study without randomization documentation."""
        assessor = WWCQualityAssessor()
        extracted_data = {
            "baseline_n": 100,
            "endline_n": 95,
            "methodology": "RCT",
            "randomization_documented": False,
        }
        user_judgments = {"chosen_attrition_boundary": "cautious"}

        assessment = assessor.assess(extracted_data, user_judgments)

        assert assessment.final_rating == WWCRating.DOES_NOT_MEET
        assert "Randomization" in assessment.rating_justification[0]

    def test_high_attrition_no_baseline_equivalence_does_not_meet(self):
        """Test high-attrition study without baseline equivalence."""
        assessor = WWCQualityAssessor()
        extracted_data = {
            "baseline_n": 100,
            "endline_n": 70,
            "treatment_attrition": 0.25,
            "control_attrition": 0.30,
            "methodology": "RCT",
            "randomization_documented": True,
        }
        user_judgments = {"chosen_attrition_boundary": "cautious"}

        assessment = assessor.assess(extracted_data, user_judgments)

        assert assessment.final_rating == WWCRating.DOES_NOT_MEET
        assert assessment.is_high_attrition is True

    def test_baseline_equivalence_requires_adjustment(self):
        """Test baseline equivalence that requires adjustment but adjustment not confirmed."""
        assessor = WWCQualityAssessor()
        extracted_data = {
            "baseline_n": 100,
            "endline_n": 70,
            "treatment_attrition": 0.20,
            "control_attrition": 0.30,
            "methodology": "RCT",
            "randomization_documented": True,
            "baseline_means": {"treatment": 50.0, "control": 51.5},  # d ≈ 0.15 (adjustable range)
            "baseline_sds": {"treatment": 10.0, "control": 10.0},
        }
        user_judgments = {
            "chosen_attrition_boundary": "cautious",
            "adjustment_strategy_is_valid": False,
        }

        assessment = assessor.assess(extracted_data, user_judgments)

        assert assessment.final_rating == WWCRating.DOES_NOT_MEET
        # Check that the justification mentions adjustment
        justification_text = " ".join(assessment.rating_justification).lower()
        assert "adjustment" in justification_text

    def test_quasi_experimental_requires_baseline_check(self):
        """Test that quasi-experimental designs require baseline equivalence check."""
        assessor = WWCQualityAssessor()
        extracted_data = {
            "baseline_n": 100,
            "endline_n": 95,
            "treatment_attrition": 0.03,
            "control_attrition": 0.05,
            "methodology": "Quasi-experimental",
            "randomization_documented": None,
            "baseline_means": {"treatment": 50.0, "control": 51.0},
            "baseline_sds": {"treatment": 10.0, "control": 10.0},
        }
        user_judgments = {
            "chosen_attrition_boundary": "cautious",
            "randomization_documented": True,  # User judgment
        }

        assessment = assessor.assess(extracted_data, user_judgments)

        # Should check baseline equivalence even though attrition is low
        assert assessment.baseline_effect_size is not None
        assert assessment.is_rct is False

    def test_assessment_to_dict(self):
        """Test conversion of assessment to dictionary."""
        assessor = WWCQualityAssessor()
        extracted_data = {
            "baseline_n": 100,
            "endline_n": 95,
            "treatment_attrition": 0.04,
            "control_attrition": 0.06,
            "methodology": "RCT",
            "randomization_documented": True,
            "paper_id": 1,
            "paper_title": "Test Paper",
        }
        user_judgments = {"chosen_attrition_boundary": "cautious"}

        assessment = assessor.assess(extracted_data, user_judgments)
        result_dict = assessor.assessment_to_dict(assessment)

        assert result_dict["paper_id"] == 1
        assert result_dict["paper_title"] == "Test Paper"
        assert result_dict["final_rating"] == WWCRating.MEETS_WITHOUT_RESERVATIONS.value
        assert "chosen_attrition_boundary" in result_dict
        assert "rating_justification" in result_dict
        assert isinstance(result_dict["rating_justification"], list)

    def test_invalid_attrition_boundary_defaults_to_cautious(self):
        """Test that invalid attrition boundary defaults to cautious."""
        assessor = WWCQualityAssessor()
        extracted_data = {
            "baseline_n": 100,
            "endline_n": 95,
            "treatment_attrition": 0.04,
            "control_attrition": 0.06,
            "methodology": "RCT",
            "randomization_documented": True,
        }
        user_judgments = {"chosen_attrition_boundary": "invalid_value"}

        assessment = assessor.assess(extracted_data, user_judgments)

        assert assessment.chosen_attrition_boundary == AttritionBoundary.CAUTIOUS

