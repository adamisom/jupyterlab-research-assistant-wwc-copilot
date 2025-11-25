"""WWC Quality Assessment Engine implementing WWC Handbook v5.0 standards."""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import ClassVar, Optional

logger = logging.getLogger(__name__)


class WWCRating(Enum):
    """WWC quality rating levels."""

    MEETS_WITHOUT_RESERVATIONS = "Meets WWC Standards Without Reservations"
    MEETS_WITH_RESERVATIONS = "Meets WWC Standards With Reservations"
    DOES_NOT_MEET = "Does Not Meet WWC Standards"


class AttritionBoundary(Enum):
    """Attrition boundary types from WWC Handbook."""

    OPTIMISTIC = "optimistic"
    CAUTIOUS = "cautious"


@dataclass
class WWCAssessment:
    """Complete WWC assessment result for a study."""

    # --- Fields requiring human judgment ---
    chosen_attrition_boundary: AttritionBoundary = AttritionBoundary.CAUTIOUS
    adjustment_strategy_is_valid: Optional[bool] = None
    randomization_documented: Optional[bool] = None  # Human judgment if not clear from text

    # --- Fields for automated extraction & calculation ---
    is_rct: bool = True
    overall_attrition: Optional[float] = None  # Calculated: (baseline_n - endline_n) / baseline_n
    differential_attrition: Optional[float] = None  # Calculated: |treatment_attrition - control_attrition|
    is_high_attrition: Optional[bool] = None
    baseline_effect_size: Optional[float] = None  # Cohen's d for baseline equivalence
    baseline_equivalence_satisfied: Optional[bool] = None

    # --- Final Rating ---
    final_rating: WWCRating = WWCRating.DOES_NOT_MEET
    rating_justification: list[str] = field(default_factory=list)

    # --- Additional metadata ---
    paper_id: Optional[int] = None
    paper_title: Optional[str] = None


class WWCQualityAssessor:
    """
    Implements WWC Handbook v5.0 decision rules for quality assessment.

    Key rules:
    1. Randomization must be documented
    2. Attrition thresholds depend on boundary (cautious vs optimistic)
    3. Baseline equivalence required for QEDs and high-attrition RCTs
    4. Statistical adjustments must be valid
    """

    # Attrition boundaries from WWC Handbook Appendix C
    # Dictionary format: {overall_attrition_threshold: max_differential_attrition}
    ATTRITION_BOUNDARIES: ClassVar[dict] = {
        "cautious": {
            0.10: 0.05,  # ≤10% overall → ≤5% differential
            0.20: 0.03,  # ≤20% overall → ≤3% differential
            0.30: 0.01,  # ≤30% overall → ≤1% differential
            0.40: 0.00,  # ≤40% overall → 0% differential
        },
        "optimistic": {
            0.10: 0.07,  # ≤10% overall → ≤7% differential
            0.20: 0.05,  # ≤20% overall → ≤5% differential
            0.30: 0.03,  # ≤30% overall → ≤3% differential
            0.40: 0.01,  # ≤40% overall → ≤1% differential
        },
    }

    # Baseline equivalence thresholds (Cohen's d)
    BASELINE_EQUIVALENCE_THRESHOLDS: ClassVar[dict] = {
        "equivalent": 0.05,  # ≤0.05 SD: equivalent, no adjustment required
        "adjustable": 0.25,  # >0.05 and ≤0.25 SD: adjustment required
        "not_equivalent": 0.25,  # >0.25 SD: does not meet standards
    }

    def is_low_attrition(
        self, overall: float, differential: float, boundary: AttritionBoundary
    ) -> bool:
        """
        Determine if attrition is low based on WWC boundaries.

        Args:
            overall: Overall attrition rate (0.0 to 1.0)
            differential: Differential attrition rate (0.0 to 1.0)
            boundary: Cautious or optimistic boundary

        Returns:
            True if attrition is low (meets WWC standards)
        """
        if overall is None or differential is None:
            return False

        if overall > 0.40:
            return False  # >40% overall attrition always fails

        boundary_table = self.ATTRITION_BOUNDARIES[boundary.value]

        # Check thresholds in order (lowest to highest)
        for overall_threshold, diff_threshold in sorted(boundary_table.items()):
            if overall <= overall_threshold:
                return differential <= diff_threshold

        return False

    def calculate_baseline_equivalence(
        self,
        treatment_mean: float,
        control_mean: float,
        treatment_sd: float,
        control_sd: float,
    ) -> dict:
        """
        Calculate baseline equivalence effect size (Cohen's d).

        Args:
            treatment_mean: Treatment group baseline mean
            control_mean: Control group baseline mean
            treatment_sd: Treatment group baseline standard deviation
            control_sd: Control group baseline standard deviation

        Returns:
            Dictionary with 'effect_size' (Cohen's d) and 'status' (equivalent/adjustable/not_equivalent)
        """
        # Pooled standard deviation
        pooled_sd = ((treatment_sd**2 + control_sd**2) / 2) ** 0.5

        if pooled_sd == 0:
            return {
                "effect_size": 0.0,
                "status": "equivalent",
                "message": "No variance in baseline measures",
            }

        # Cohen's d
        d = (treatment_mean - control_mean) / pooled_sd

        # Determine status
        abs_d = abs(d)
        if abs_d <= self.BASELINE_EQUIVALENCE_THRESHOLDS["equivalent"]:
            status = "equivalent"
            message = "Baseline groups are equivalent (≤0.05 SD difference)"
        elif abs_d <= self.BASELINE_EQUIVALENCE_THRESHOLDS["adjustable"]:
            status = "adjustable"
            message = (
                "Baseline groups require statistical adjustment (>0.05 and ≤0.25 SD difference)"
            )
        else:
            status = "not_equivalent"
            message = "Baseline groups are not equivalent (>0.25 SD difference)"

        return {"effect_size": d, "status": status, "message": message}

    def assess(self, extracted_data: dict, user_judgments: dict) -> WWCAssessment:
        """
        Perform complete WWC assessment for a study.

        Args:
            extracted_data: Automatically extracted study data (from database/AI)
                - baseline_n: Baseline sample size
                - endline_n: Endline sample size
                - treatment_attrition: Treatment group attrition rate (0.0 to 1.0)
                - control_attrition: Control group attrition rate (0.0 to 1.0)
                - methodology: "RCT" or "Quasi-experimental"
                - randomization_documented: Boolean (if available from extraction)
                - baseline_means: Dict with treatment/control baseline means (optional)
                - baseline_sds: Dict with treatment/control baseline SDs (optional)
            user_judgments: User-provided judgments
                - chosen_attrition_boundary: "cautious" or "optimistic"
                - adjustment_strategy_is_valid: Boolean (if adjustment was used)
                - randomization_documented: Boolean (if not clear from extraction)

        Returns:
            WWCAssessment object with complete rating and justification
        """
        # Initialize assessment with user judgments
        boundary_str = user_judgments.get("chosen_attrition_boundary", "cautious")
        try:
            boundary = AttritionBoundary(boundary_str)
        except ValueError:
            logger.warning(f"Invalid attrition boundary: {boundary_str}, using cautious")
            boundary = AttritionBoundary.CAUTIOUS

        assessment = WWCAssessment(
            chosen_attrition_boundary=boundary,
            adjustment_strategy_is_valid=user_judgments.get("adjustment_strategy_is_valid"),
            randomization_documented=user_judgments.get(
                "randomization_documented",
                extracted_data.get("randomization_documented"),
            ),
            is_rct=(extracted_data.get("methodology", "").upper() == "RCT"),
            paper_id=extracted_data.get("paper_id"),
            paper_title=extracted_data.get("paper_title"),
        )

        assessment.rating_justification = []

        # Step 1: Check randomization documentation
        if assessment.randomization_documented is False:
            assessment.final_rating = WWCRating.DOES_NOT_MEET
            assessment.rating_justification.append(
                "Randomization was not documented or not properly described."
            )
            return assessment

        # Step 2: Calculate attrition rates
        baseline_n = extracted_data.get("baseline_n")
        endline_n = extracted_data.get("endline_n")
        treatment_attrition_rate = extracted_data.get("treatment_attrition")
        control_attrition_rate = extracted_data.get("control_attrition")

        if baseline_n and endline_n and baseline_n > 0:
            assessment.overall_attrition = (baseline_n - endline_n) / baseline_n
        elif treatment_attrition_rate is not None and control_attrition_rate is not None:
            # Approximate overall attrition as average if not directly available
            assessment.overall_attrition = (treatment_attrition_rate + control_attrition_rate) / 2

        if treatment_attrition_rate is not None and control_attrition_rate is not None:
            assessment.differential_attrition = abs(treatment_attrition_rate - control_attrition_rate)

        # Step 3: Determine if attrition is high
        if (
            assessment.overall_attrition is not None
            and assessment.differential_attrition is not None
        ):
            assessment.is_high_attrition = not self.is_low_attrition(
                assessment.overall_attrition,
                assessment.differential_attrition,
                assessment.chosen_attrition_boundary,
            )
        else:
            assessment.is_high_attrition = None
            assessment.rating_justification.append(
                "Warning: Attrition data incomplete. Assessment may be inaccurate."
            )

        # Step 4: Check baseline equivalence (required for QEDs or high-attrition RCTs)
        requires_baseline_check = (
            not assessment.is_rct or (assessment.is_high_attrition is True)
        )

        if requires_baseline_check:
            baseline_means = extracted_data.get("baseline_means", {})
            baseline_sds = extracted_data.get("baseline_sds", {})

            treatment_mean = baseline_means.get("treatment")
            control_mean = baseline_means.get("control")
            treatment_sd = baseline_sds.get("treatment")
            control_sd = baseline_sds.get("control")

            if all(v is not None for v in [treatment_mean, control_mean, treatment_sd, control_sd]):
                baseline_result = self.calculate_baseline_equivalence(
                    treatment_mean, control_mean, treatment_sd, control_sd
                )
                assessment.baseline_effect_size = baseline_result["effect_size"]

                if baseline_result["status"] == "not_equivalent":
                    assessment.final_rating = WWCRating.DOES_NOT_MEET
                    assessment.rating_justification.append(baseline_result["message"])
                    return assessment
                elif baseline_result["status"] == "adjustable":
                    # Check if valid adjustment was used
                    if assessment.adjustment_strategy_is_valid is not True:
                        assessment.final_rating = WWCRating.DOES_NOT_MEET
                        assessment.rating_justification.append(
                            f"{baseline_result['message']} Valid statistical adjustment required but not confirmed."
                        )
                        return assessment
                    else:
                        assessment.baseline_equivalence_satisfied = True
                        assessment.rating_justification.append(
                            f"{baseline_result['message']} Valid statistical adjustment confirmed."
                        )
                else:  # equivalent
                    assessment.baseline_equivalence_satisfied = True
                    assessment.rating_justification.append(baseline_result["message"])
            else:
                assessment.rating_justification.append(
                    "Warning: Baseline equivalence data incomplete. Assessment may be inaccurate."
                )

        # Step 5: Determine final rating
        if assessment.is_high_attrition is False:
            # Low attrition → Meets Without Reservations
            assessment.final_rating = WWCRating.MEETS_WITHOUT_RESERVATIONS
            assessment.rating_justification.append(
                f"Low attrition (overall: {assessment.overall_attrition:.1%}, "
                f"differential: {assessment.differential_attrition:.1%}) meets WWC standards."
            )
        elif assessment.is_high_attrition is True:
            if assessment.baseline_equivalence_satisfied is True:
                # High attrition but baseline equivalence satisfied → Meets With Reservations
                assessment.final_rating = WWCRating.MEETS_WITH_RESERVATIONS
                assessment.rating_justification.append(
                    f"High attrition (overall: {assessment.overall_attrition:.1%}, "
                    f"differential: {assessment.differential_attrition:.1%}) but baseline equivalence satisfied."
                )
            else:
                # High attrition and baseline equivalence not satisfied → Does Not Meet
                assessment.final_rating = WWCRating.DOES_NOT_MEET
                assessment.rating_justification.append(
                    f"High attrition (overall: {assessment.overall_attrition:.1%}, "
                    f"differential: {assessment.differential_attrition:.1%}) and baseline equivalence not satisfied."
                )
        else:
            # Attrition data incomplete
            assessment.final_rating = WWCRating.DOES_NOT_MEET
            assessment.rating_justification.append("Insufficient data to complete WWC assessment.")

        return assessment

    def assessment_to_dict(self, assessment: WWCAssessment) -> dict:
        """Convert WWCAssessment to dictionary for JSON serialization."""
        return {
            "paper_id": assessment.paper_id,
            "paper_title": assessment.paper_title,
            "chosen_attrition_boundary": assessment.chosen_attrition_boundary.value,
            "adjustment_strategy_is_valid": assessment.adjustment_strategy_is_valid,
            "randomization_documented": assessment.randomization_documented,
            "is_rct": assessment.is_rct,
            "overall_attrition": assessment.overall_attrition,
            "differential_attrition": assessment.differential_attrition,
            "is_high_attrition": assessment.is_high_attrition,
            "baseline_effect_size": assessment.baseline_effect_size,
            "baseline_equivalence_satisfied": assessment.baseline_equivalence_satisfied,
            "final_rating": assessment.final_rating.value,
            "rating_justification": assessment.rating_justification,
        }



