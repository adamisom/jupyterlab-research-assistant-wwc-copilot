# WWC Co-Pilot & Synthesis Engine Implementation Guide

**Purpose**: Step-by-step implementation guide for Stage 2: WWC Co-Pilot & Synthesis Engine.

**⚠️ Prerequisites**: Stage 1 (Research Library) must be 100% complete before starting Stage 2.

**Project Name**: `jupyterlab-research-assistant-wwc-copilot`  
**Python Package**: `jupyterlab_research_assistant_wwc_copilot`  
**Plugin ID**: `jupyterlab-research-assistant-wwc-copilot:plugin`  
**API Route Prefix**: `/jupyterlab-research-assistant-wwc-copilot`

---

## Table of Contents

1. [Project Structure](#project-structure)
2. [Development Workflow](#development-workflow)
3. [Stage 2: WWC Co-Pilot - Backend](#stage-2-wwc-co-pilot-backend)
4. [Stage 2: WWC Co-Pilot - Frontend](#stage-2-wwc-co-pilot-frontend)
5. [Testing Checkpoints](#testing-checkpoints)
6. [Common Issues & Solutions](#common-issues--solutions)

---

## Project Structure

### Updated Directory Layout

```
jupyterlab-research-assistant-wwc-copilot/
├── jupyterlab_research_assistant_wwc_copilot/  # Python package
│   ├── __init__.py                              # Server extension entry point
│   ├── routes.py                                # API handlers (add WWC routes)
│   ├── services/                                 # Business logic
│   │   ├── __init__.py
│   │   ├── semantic_scholar.py                  # (Stage 1)
│   │   ├── pdf_parser.py                        # (Stage 1)
│   │   ├── ai_extractor.py                      # (Stage 1)
│   │   ├── db_manager.py                        # (Stage 1)
│   │   ├── wwc_assessor.py                      # NEW: WWC assessment logic
│   │   ├── meta_analyzer.py                     # NEW: Meta-analysis engine
│   │   ├── visualizer.py                        # NEW: Forest plot generation
│   │   └── conflict_detector.py                 # NEW: NLI conflict detection
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py                            # (Stage 1 - may need WWC fields)
│   │   └── migrations/
│   └── tests/
│       ├── __init__.py
│       ├── test_routes.py                       # (Stage 1)
│       ├── test_wwc_assessor.py                 # NEW
│       ├── test_meta_analyzer.py                # NEW
│       └── test_conflict_detector.py            # NEW
├── src/                                         # TypeScript frontend
│   ├── index.ts                                 # Plugin entry point
│   ├── request.ts                               # API client helper
│   ├── api.ts                                   # Typed API functions (add WWC functions)
│   ├── widgets/
│   │   ├── ResearchLibraryPanel.tsx              # (Stage 1 - add multi-select)
│   │   ├── DiscoveryTab.tsx                     # (Stage 1)
│   │   ├── LibraryTab.tsx                       # (Stage 1 - add multi-select)
│   │   ├── PaperCard.tsx                        # (Stage 1 - add checkbox)
│   │   ├── DetailView.tsx                       # (Stage 1)
│   │   ├── WWCCoPilot.tsx                       # NEW: WWC assessment UI
│   │   ├── SynthesisWorkbench.tsx               # NEW: Main synthesis widget
│   │   ├── MetaAnalysisView.tsx                 # NEW: Meta-analysis results
│   │   └── ConflictView.tsx                      # NEW: Conflict detection results
│   └── __tests__/
└── docs/
```

---

## Development Workflow

### Initial Setup (One-Time)

```bash
# 1. Activate your environment
conda activate <your-env>  # or: source venv/bin/activate

# 2. Install new dependencies
pip install statsmodels matplotlib transformers torch  # For meta-analysis, plots, NLI

# 3. Rebuild extension
jlpm build
pip install -e .
jupyter labextension develop . --overwrite
jupyter server extension enable jupyterlab_research_assistant_wwc_copilot

# 4. Restart JupyterLab
jupyter lab
```

### Rapid Iteration Cycle

**For TypeScript/Frontend changes:**
```bash
# Terminal 1: Watch mode (auto-rebuilds on save)
jlpm watch

# Terminal 2: Run JupyterLab
jupyter lab

# After saving TypeScript files: Just refresh browser (Cmd+R / Ctrl+R)
```

**For Python/Backend changes:**
```bash
# Make your changes, then restart JupyterLab
# Press Ctrl+C in terminal, then:
jupyter lab
```

**Manual Testing Checkpoint:**
- After each feature: Test in browser, check console for errors
- After each API endpoint: Test with curl or browser dev tools
- After each UI component: Verify it renders and responds to interactions

---

## Stage 2: WWC Co-Pilot - Backend

### Phase 2.1: WWC Assessment Engine

**File**: `jupyterlab_research_assistant_wwc_copilot/services/wwc_assessor.py`

```python
"""WWC Quality Assessment Engine implementing WWC Handbook v5.0 standards."""

from dataclasses import dataclass, field
from typing import Optional, Dict, List
from enum import Enum
import logging

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
    rating_justification: List[str] = field(default_factory=list)
    
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
    # Format: {overall_attrition_threshold: max_differential_attrition}
    ATTRITION_BOUNDARIES = {
        "cautious": {
            0.10: 0.05,  # ≤10% overall → ≤5% differential
            0.20: 0.03,  # ≤20% overall → ≤3% differential
            0.30: 0.01,  # ≤30% overall → ≤1% differential
            0.40: 0.00   # ≤40% overall → 0% differential
        },
        "optimistic": {
            0.10: 0.07,  # ≤10% overall → ≤7% differential
            0.20: 0.05,  # ≤20% overall → ≤5% differential
            0.30: 0.03,  # ≤30% overall → ≤3% differential
            0.40: 0.01   # ≤40% overall → ≤1% differential
        }
    }
    
    # Baseline equivalence thresholds (Cohen's d)
    BASELINE_EQUIVALENCE_THRESHOLDS = {
        "equivalent": 0.05,      # ≤0.05 SD: equivalent, no adjustment required
        "adjustable": 0.25,      # >0.05 and ≤0.25 SD: adjustment required
        "not_equivalent": 0.25  # >0.25 SD: does not meet standards
    }
    
    def is_low_attrition(
        self,
        overall: float,
        differential: float,
        boundary: AttritionBoundary
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
        control_sd: float
    ) -> Dict:
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
        pooled_sd = ((treatment_sd ** 2 + control_sd ** 2) / 2) ** 0.5
        
        if pooled_sd == 0:
            return {
                "effect_size": 0.0,
                "status": "equivalent",
                "message": "No variance in baseline measures"
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
            message = "Baseline groups require statistical adjustment (>0.05 and ≤0.25 SD difference)"
        else:
            status = "not_equivalent"
            message = "Baseline groups are not equivalent (>0.25 SD difference)"
        
        return {
            "effect_size": d,
            "status": status,
            "message": message
        }
    
    def assess(
        self,
        extracted_data: Dict,
        user_judgments: Dict
    ) -> WWCAssessment:
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
        assessment = WWCAssessment(
            chosen_attrition_boundary=AttritionBoundary(
                user_judgments.get("chosen_attrition_boundary", "cautious")
            ),
            adjustment_strategy_is_valid=user_judgments.get("adjustment_strategy_is_valid"),
            randomization_documented=user_judgments.get(
                "randomization_documented",
                extracted_data.get("randomization_documented")
            ),
            is_rct=(extracted_data.get("methodology", "").upper() == "RCT"),
            paper_id=extracted_data.get("paper_id"),
            paper_title=extracted_data.get("paper_title")
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
        if assessment.overall_attrition is not None and assessment.differential_attrition is not None:
            assessment.is_high_attrition = not self.is_low_attrition(
                assessment.overall_attrition,
                assessment.differential_attrition,
                assessment.chosen_attrition_boundary
            )
        else:
            assessment.is_high_attrition = None
            assessment.rating_justification.append(
                "Warning: Attrition data incomplete. Assessment may be inaccurate."
            )
        
        # Step 4: Check baseline equivalence (required for QEDs or high-attrition RCTs)
        requires_baseline_check = (
            not assessment.is_rct or
            (assessment.is_high_attrition is True)
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
            assessment.rating_justification.append(
                "Insufficient data to complete WWC assessment."
            )
        
        return assessment
    
    def assessment_to_dict(self, assessment: WWCAssessment) -> Dict:
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
            "rating_justification": assessment.rating_justification
        }
```

**Dependencies to add to `pyproject.toml`:**
```toml
dependencies = [
    # ... existing dependencies ...
    "statsmodels>=0.14.0",  # For meta-analysis
    "matplotlib>=3.7.0",    # For forest plots
    "numpy>=1.24.0",        # For statistical calculations
]
```

**Manual Testing Checkpoint:**
```python
# In a Jupyter notebook:
from jupyterlab_research_assistant_wwc_copilot.services.wwc_assessor import (
    WWCQualityAssessor,
    AttritionBoundary
)

assessor = WWCQualityAssessor()

# Test case 1: Low attrition RCT
extracted_data = {
    "baseline_n": 100,
    "endline_n": 95,
    "treatment_attrition": 0.04,
    "control_attrition": 0.06,
    "methodology": "RCT",
    "randomization_documented": True
}
user_judgments = {"chosen_attrition_boundary": "cautious"}

assessment = assessor.assess(extracted_data, user_judgments)
print(f"Rating: {assessment.final_rating.value}")
print(f"Justification: {assessment.rating_justification}")

# Test case 2: High attrition with baseline equivalence
extracted_data2 = {
    "baseline_n": 100,
    "endline_n": 70,
    "treatment_attrition": 0.20,
    "control_attrition": 0.30,
    "methodology": "RCT",
    "randomization_documented": True,
    "baseline_means": {"treatment": 50.0, "control": 51.0},
    "baseline_sds": {"treatment": 10.0, "control": 10.0}
}
user_judgments2 = {
    "chosen_attrition_boundary": "cautious",
    "adjustment_strategy_is_valid": True
}

assessment2 = assessor.assess(extracted_data2, user_judgments2)
print(f"Rating: {assessment2.final_rating.value}")
```

### Phase 2.2: Meta-Analysis Engine

**File**: `jupyterlab_research_assistant_wwc_copilot/services/meta_analyzer.py`

```python
"""Meta-analysis engine using statsmodels for random-effects models."""

import numpy as np
import statsmodels.stats.meta_analysis as meta
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class MetaAnalyzer:
    """
    Performs random-effects meta-analysis on study effect sizes.
    
    Uses DerSimonian-Laird estimator (default in statsmodels) for
    between-study variance (tau-squared).
    """
    
    def perform_random_effects_meta_analysis(
        self,
        studies: List[Dict]
    ) -> Dict:
        """
        Perform random-effects meta-analysis.
        
        Args:
            studies: List of study dictionaries, each containing:
                - effect_size: Effect size (Cohen's d, Hedges' g, etc.)
                - std_error: Standard error of effect size
                - study_label: Optional label for the study (e.g., paper title)
                - paper_id: Optional paper ID
        
        Returns:
            Dictionary with:
                - pooled_effect: Pooled effect size estimate
                - ci_lower: Lower bound of 95% confidence interval
                - ci_upper: Upper bound of 95% confidence interval
                - p_value: P-value for test of null hypothesis (effect = 0)
                - tau_squared: Between-study variance estimate
                - i_squared: I² statistic (heterogeneity measure)
                - q_statistic: Q statistic for heterogeneity test
                - q_p_value: P-value for Q statistic
                - studies: List of individual study results with weights
        """
        if len(studies) < 2:
            raise ValueError("Meta-analysis requires at least 2 studies")
        
        # Extract effect sizes and standard errors
        effect_sizes = np.array([s["effect_size"] for s in studies])
        std_errors = np.array([s["std_error"] for s in studies])
        
        # Validate inputs
        if np.any(std_errors <= 0):
            raise ValueError("Standard errors must be positive")
        
        # Perform random-effects meta-analysis using DerSimonian-Laird estimator
        try:
            result = meta.combine_effects(
                effect_sizes,
                std_errors,
                method_re="DL",  # DerSimonian-Laird
                use_t=True  # Use t-distribution for confidence intervals
            )
            
            # Calculate heterogeneity statistics
            het_test = result.het_test()
            
            # Calculate I² (percentage of total variation due to heterogeneity)
            q_statistic = het_test.statistic
            df = len(studies) - 1
            if df > 0 and q_statistic > df:
                i_squared = ((q_statistic - df) / q_statistic) * 100
            else:
                i_squared = 0.0
            
            # Calculate study weights (inverse variance weights)
            weights = 1.0 / (std_errors ** 2 + result.tau2)
            weights = weights / weights.sum()  # Normalize to sum to 1
            
            # Prepare individual study results
            study_results = []
            for i, study in enumerate(studies):
                study_results.append({
                    "paper_id": study.get("paper_id"),
                    "study_label": study.get("study_label", f"Study {i+1}"),
                    "effect_size": float(effect_sizes[i]),
                    "std_error": float(std_errors[i]),
                    "weight": float(weights[i]),
                    "ci_lower": float(effect_sizes[i] - 1.96 * std_errors[i]),
                    "ci_upper": float(effect_sizes[i] + 1.96 * std_errors[i])
                })
            
            return {
                "pooled_effect": float(result.effect),
                "ci_lower": float(result.conf_int()[0]),
                "ci_upper": float(result.conf_int()[1]),
                "p_value": float(result.pvalue),
                "tau_squared": float(result.tau2),
                "i_squared": float(i_squared),
                "q_statistic": float(q_statistic),
                "q_p_value": float(het_test.pvalue),
                "n_studies": len(studies),
                "studies": study_results
            }
        except Exception as e:
            logger.error(f"Meta-analysis failed: {str(e)}")
            raise Exception(f"Meta-analysis computation error: {str(e)}")
    
    def interpret_heterogeneity(self, i_squared: float) -> str:
        """
        Interpret I² statistic using Higgins et al. (2003) guidelines.
        
        Args:
            i_squared: I² statistic (0-100)
        
        Returns:
            Interpretation string
        """
        if i_squared < 25:
            return "Low heterogeneity"
        elif i_squared < 50:
            return "Moderate heterogeneity"
        elif i_squared < 75:
            return "Substantial heterogeneity"
        else:
            return "Considerable heterogeneity"
```

**Manual Testing Checkpoint:**
```python
# In a Jupyter notebook:
from jupyterlab_research_assistant_wwc_copilot.services.meta_analyzer import MetaAnalyzer

analyzer = MetaAnalyzer()

# Example studies
studies = [
    {"effect_size": 0.5, "std_error": 0.15, "study_label": "Study A", "paper_id": 1},
    {"effect_size": 0.3, "std_error": 0.12, "study_label": "Study B", "paper_id": 2},
    {"effect_size": 0.7, "std_error": 0.18, "study_label": "Study C", "paper_id": 3},
]

result = analyzer.perform_random_effects_meta_analysis(studies)
print(f"Pooled effect: {result['pooled_effect']:.3f}")
print(f"95% CI: [{result['ci_lower']:.3f}, {result['ci_upper']:.3f}]")
print(f"I²: {result['i_squared']:.1f}% - {analyzer.interpret_heterogeneity(result['i_squared'])}")
```

### Phase 2.3: Forest Plot Generator

**File**: `jupyterlab_research_assistant_wwc_copilot/services/visualizer.py`

```python
"""Forest plot generation using matplotlib."""

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict, Optional
import io
import base64
import logging

logger = logging.getLogger(__name__)


class Visualizer:
    """Generates forest plots for meta-analysis results."""
    
    def create_forest_plot(
        self,
        studies: List[Dict],
        pooled_effect: float,
        ci_lower: float,
        ci_upper: float,
        title: str = "Forest Plot of Study Effect Sizes",
        figsize: tuple = (10, 8),
        dpi: int = 100
    ) -> str:
        """
        Generate a forest plot and return as base64-encoded PNG.
        
        Args:
            studies: List of study dictionaries with:
                - effect_size: Individual study effect size
                - ci_lower: Lower CI bound
                - ci_upper: Upper CI bound
                - study_label: Label for the study
            pooled_effect: Pooled effect size from meta-analysis
            ci_lower: Lower CI bound for pooled effect
            ci_upper: Upper CI bound for pooled effect
            title: Plot title
            figsize: Figure size (width, height) in inches
            dpi: Resolution in dots per inch
        
        Returns:
            Base64-encoded PNG image string
        """
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
        
        n_studies = len(studies)
        y_positions = np.arange(n_studies + 1)  # +1 for pooled effect row
        
        # Plot individual studies
        for i, study in enumerate(studies):
            y_pos = y_positions[i]
            effect = study["effect_size"]
            ci_low = study["ci_lower"]
            ci_high = study["ci_upper"]
            
            # Plot point estimate
            ax.plot(effect, y_pos, 'o', markersize=8, color='steelblue')
            
            # Plot confidence interval
            ax.plot([ci_low, ci_high], [y_pos, y_pos], 'b-', linewidth=2)
            
            # Add study label
            label = study.get("study_label", f"Study {i+1}")
            ax.text(-0.5, y_pos, label, va='center', ha='right', fontsize=9)
        
        # Plot pooled effect (diamond shape)
        pooled_y = y_positions[-1]
        ax.plot(pooled_effect, pooled_y, 'D', markersize=12, color='red', label='Pooled Effect')
        ax.plot([ci_lower, ci_upper], [pooled_y, pooled_y], 'r-', linewidth=3)
        
        # Add vertical line at effect = 0
        ax.axvline(x=0, color='black', linestyle='--', linewidth=1, alpha=0.5)
        
        # Add vertical line at pooled effect
        ax.axvline(x=pooled_effect, color='red', linestyle=':', linewidth=1, alpha=0.5)
        
        # Labels and formatting
        ax.set_xlabel('Effect Size (Cohen\'s d)', fontsize=11)
        ax.set_ylabel('Study', fontsize=11)
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.set_yticks(y_positions)
        ax.set_yticklabels([s.get("study_label", f"Study {i+1}") for i, s in enumerate(studies)] + ['Pooled Effect'])
        ax.grid(True, alpha=0.3, axis='x')
        ax.legend(loc='best')
        
        # Add text annotation for pooled effect
        ax.text(
            pooled_effect + 0.1,
            pooled_y,
            f'd = {pooled_effect:.3f} [{ci_lower:.3f}, {ci_upper:.3f}]',
            va='center',
            fontsize=9,
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        )
        
        plt.tight_layout()
        
        # Convert to base64
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', dpi=dpi)
        plt.close(fig)
        buf.seek(0)
        
        image_base64 = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()
        
        return image_base64
```

**Manual Testing Checkpoint:**
```python
# In a Jupyter notebook:
from jupyterlab_research_assistant_wwc_copilot.services.visualizer import Visualizer

visualizer = Visualizer()

studies = [
    {"effect_size": 0.5, "ci_lower": 0.2, "ci_upper": 0.8, "study_label": "Study A"},
    {"effect_size": 0.3, "ci_lower": 0.1, "ci_upper": 0.5, "study_label": "Study B"},
    {"effect_size": 0.7, "ci_lower": 0.4, "ci_upper": 1.0, "study_label": "Study C"},
]

image_base64 = visualizer.create_forest_plot(
    studies,
    pooled_effect=0.5,
    ci_lower=0.3,
    ci_upper=0.7
)

# Save to file to view
with open('/tmp/forest_plot.png', 'wb') as f:
    import base64
    f.write(base64.b64decode(image_base64))
print("Forest plot saved to /tmp/forest_plot.png")
```

### Phase 2.4: Conflict Detection (Optional - Advanced)

**File**: `jupyterlab_research_assistant_wwc_copilot/services/conflict_detector.py`

```python
"""Conflict detection using Natural Language Inference (NLI) models."""

from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

# Optional: Only import if transformers is available
try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("transformers library not available. Conflict detection will be disabled.")


class ConflictDetector:
    """
    Detects contradictions between study findings using NLI models.
    
    Uses a pre-trained NLI model (e.g., DeBERTa fine-tuned on MNLI)
    to identify contradictory findings across papers.
    """
    
    def __init__(self, model_name: str = "cross-encoder/nli-deberta-v3-base"):
        """
        Initialize NLI pipeline.
        
        Args:
            model_name: Hugging Face model identifier for NLI model
        """
        self.model_name = model_name
        self.nli_pipeline = None
        
        if TRANSFORMERS_AVAILABLE:
            try:
                self.nli_pipeline = pipeline(
                    "text-classification",
                    model=model_name,
                    device=-1  # Use CPU (-1), set to 0 for GPU if available
                )
                logger.info(f"Loaded NLI model: {model_name}")
            except Exception as e:
                logger.error(f"Failed to load NLI model: {str(e)}")
                self.nli_pipeline = None
        else:
            logger.warning("transformers not available. Conflict detection disabled.")
    
    def find_contradictions(
        self,
        findings1: List[str],
        findings2: List[str],
        confidence_threshold: float = 0.8
    ) -> List[Dict]:
        """
        Compare two lists of findings and identify contradictions.
        
        Args:
            findings1: List of finding statements from first study
            findings2: List of finding statements from second study
            confidence_threshold: Minimum confidence score for contradiction (0.0 to 1.0)
        
        Returns:
            List of contradiction dictionaries with:
                - finding1: First finding statement
                - finding2: Second finding statement
                - confidence: Confidence score (0.0 to 1.0)
                - label: NLI label (contradiction/entailment/neutral)
        """
        if self.nli_pipeline is None:
            logger.warning("NLI pipeline not available. Returning empty results.")
            return []
        
        contradictions = []
        
        for f1 in findings1:
            for f2 in findings2:
                try:
                    # Format for NLI: premise [SEP] hypothesis
                    result = self.nli_pipeline(f"{f1} [SEP] {f2}")
                    
                    # Handle different return formats
                    if isinstance(result, list) and len(result) > 0:
                        result = result[0]
                    
                    label = result.get("label", "").lower()
                    score = result.get("score", 0.0)
                    
                    # Check for contradiction
                    if "contradict" in label and score >= confidence_threshold:
                        contradictions.append({
                            "finding1": f1,
                            "finding2": f2,
                            "confidence": float(score),
                            "label": label
                        })
                except Exception as e:
                    logger.error(f"Error processing findings: {str(e)}")
                    continue
        
        return contradictions
    
    def extract_key_findings(self, paper_text: str, max_findings: int = 5) -> List[str]:
        """
        Extract key findings from paper text (simple keyword-based approach).
        
        This is a placeholder. In production, use AI extraction or structured data.
        
        Args:
            paper_text: Full text of the paper
            max_findings: Maximum number of findings to extract
        
        Returns:
            List of finding statements
        """
        # Simple keyword-based extraction (placeholder)
        # In production, use AI extraction or structured data from database
        findings = []
        
        # Look for common finding patterns
        keywords = ["significant", "found that", "results show", "conclusion"]
        sentences = paper_text.split('.')
        
        for sentence in sentences:
            if any(kw in sentence.lower() for kw in keywords):
                findings.append(sentence.strip())
                if len(findings) >= max_findings:
                    break
        
        return findings
```

**Note**: Conflict detection requires the `transformers` library and can be memory-intensive. Make it optional or use a lighter model.

**Dependencies to add to `pyproject.toml` (optional):**
```toml
dependencies = [
    # ... existing dependencies ...
    "transformers>=4.30.0",  # Optional: For conflict detection
    "torch>=2.0.0",          # Optional: For transformers
]
```

### Phase 2.5: API Routes for WWC & Synthesis

**Update**: `jupyterlab_research_assistant_wwc_copilot/routes.py`

Add these new handlers to the existing file:

```python
# Add to imports at top of routes.py
from .services.wwc_assessor import WWCQualityAssessor, AttritionBoundary
from .services.meta_analyzer import MetaAnalyzer
from .services.visualizer import Visualizer
from .services.conflict_detector import ConflictDetector
from .services.db_manager import DatabaseManager

# Add new handler classes

class WWCAssessmentHandler(APIHandler):
    """Handler for WWC quality assessment."""
    
    @tornado.web.authenticated
    def post(self):
        """Run WWC assessment for a paper."""
        try:
            data = self.get_json_body()
            if not data:
                self.set_status(400)
                self.finish(json.dumps({"status": "error", "message": "No data provided"}))
                return
            
            paper_id = data.get("paper_id")
            if not paper_id:
                self.set_status(400)
                self.finish(json.dumps({"status": "error", "message": "paper_id required"}))
                return
            
            # Fetch paper from database
            with DatabaseManager() as db:
                paper = db.get_paper_by_id(paper_id)
                if not paper:
                    self.set_status(404)
                    self.finish(json.dumps({"status": "error", "message": "Paper not found"}))
                    return
                
                # Prepare extracted data
                extracted_data = {
                    "paper_id": paper["id"],
                    "paper_title": paper["title"],
                    "methodology": paper.get("study_metadata", {}).get("methodology"),
                    "baseline_n": paper.get("study_metadata", {}).get("sample_size_baseline"),
                    "endline_n": paper.get("study_metadata", {}).get("sample_size_endline"),
                    "randomization_documented": None,  # Will be set from user judgment or extraction
                }
                
                # Extract attrition data if available
                # Note: This assumes attrition rates are stored in study_metadata
                # You may need to extract from full_text using AI if not available
                
                # User judgments
                user_judgments = data.get("judgments", {})
                
                # Run assessment
                assessor = WWCQualityAssessor()
                assessment = assessor.assess(extracted_data, user_judgments)
                
                # Convert to dict for JSON response
                result = assessor.assessment_to_dict(assessment)
                
                self.finish(json.dumps({"status": "success", "data": result}))
        except Exception as e:
            self.set_status(500)
            self.finish(json.dumps({"status": "error", "message": str(e)}))


class MetaAnalysisHandler(APIHandler):
    """Handler for meta-analysis."""
    
    @tornado.web.authenticated
    def post(self):
        """Perform meta-analysis on selected papers."""
        try:
            data = self.get_json_body()
            if not data:
                self.set_status(400)
                self.finish(json.dumps({"status": "error", "message": "No data provided"}))
                return
            
            paper_ids = data.get("paper_ids", [])
            outcome_name = data.get("outcome_name")  # Optional: specific outcome to analyze
            
            if len(paper_ids) < 2:
                self.set_status(400)
                self.finish(json.dumps({
                    "status": "error",
                    "message": "At least 2 papers required for meta-analysis"
                }))
                return
            
            # Fetch papers from database
            with DatabaseManager() as db:
                studies = []
                for paper_id in paper_ids:
                    paper = db.get_paper_by_id(paper_id)
                    if not paper:
                        continue
                    
                    # Extract effect sizes
                    effect_sizes = paper.get("study_metadata", {}).get("effect_sizes", {})
                    
                    if outcome_name:
                        # Use specific outcome
                        outcome_data = effect_sizes.get(outcome_name)
                        if outcome_data:
                            studies.append({
                                "paper_id": paper["id"],
                                "study_label": paper["title"],
                                "effect_size": outcome_data.get("d", 0.0),
                                "std_error": outcome_data.get("se", 0.1)
                            })
                    else:
                        # Use first available outcome
                        if effect_sizes:
                            first_outcome = list(effect_sizes.values())[0]
                            studies.append({
                                "paper_id": paper["id"],
                                "study_label": paper["title"],
                                "effect_size": first_outcome.get("d", 0.0),
                                "std_error": first_outcome.get("se", 0.1)
                            })
                
                if len(studies) < 2:
                    self.set_status(400)
                    self.finish(json.dumps({
                        "status": "error",
                        "message": "Insufficient studies with effect size data"
                    }))
                    return
                
                # Perform meta-analysis
                analyzer = MetaAnalyzer()
                result = analyzer.perform_random_effects_meta_analysis(studies)
                
                # Generate forest plot
                visualizer = Visualizer()
                forest_plot_base64 = visualizer.create_forest_plot(
                    result["studies"],
                    result["pooled_effect"],
                    result["ci_lower"],
                    result["ci_upper"],
                    title=f"Meta-Analysis: {len(studies)} Studies"
                )
                
                result["forest_plot"] = forest_plot_base64
                result["heterogeneity_interpretation"] = analyzer.interpret_heterogeneity(
                    result["i_squared"]
                )
                
                self.finish(json.dumps({"status": "success", "data": result}))
        except Exception as e:
            self.set_status(500)
            self.finish(json.dumps({"status": "error", "message": str(e)}))


class ConflictDetectionHandler(APIHandler):
    """Handler for conflict detection."""
    
    @tornado.web.authenticated
    def post(self):
        """Detect conflicts between papers."""
        try:
            data = self.get_json_body()
            if not data:
                self.set_status(400)
                self.finish(json.dumps({"status": "error", "message": "No data provided"}))
                return
            
            paper_ids = data.get("paper_ids", [])
            confidence_threshold = data.get("confidence_threshold", 0.8)
            
            if len(paper_ids) < 2:
                self.set_status(400)
                self.finish(json.dumps({
                    "status": "error",
                    "message": "At least 2 papers required for conflict detection"
                }))
                return
            
            # Fetch papers from database
            with DatabaseManager() as db:
                papers = []
                for paper_id in paper_ids:
                    paper = db.get_paper_by_id(paper_id)
                    if paper:
                        papers.append(paper)
                
                if len(papers) < 2:
                    self.set_status(400)
                    self.finish(json.dumps({
                        "status": "error",
                        "message": "Insufficient papers found"
                    }))
                    return
                
                # Extract findings (simplified - use AI extraction in production)
                detector = ConflictDetector()
                all_contradictions = []
                
                # Compare each pair of papers
                for i in range(len(papers)):
                    for j in range(i + 1, len(papers)):
                        paper1 = papers[i]
                        paper2 = papers[j]
                        
                        # Extract findings (placeholder - use AI extraction)
                        findings1 = detector.extract_key_findings(
                            paper1.get("full_text", "") or paper1.get("abstract", "")
                        )
                        findings2 = detector.extract_key_findings(
                            paper2.get("full_text", "") or paper2.get("abstract", "")
                        )
                        
                        if findings1 and findings2:
                            contradictions = detector.find_contradictions(
                                findings1,
                                findings2,
                                confidence_threshold=confidence_threshold
                            )
                            
                            for contradiction in contradictions:
                                contradiction["paper1_id"] = paper1["id"]
                                contradiction["paper1_title"] = paper1["title"]
                                contradiction["paper2_id"] = paper2["id"]
                                contradiction["paper2_title"] = paper2["title"]
                                all_contradictions.append(contradiction)
                
                self.finish(json.dumps({
                    "status": "success",
                    "data": {
                        "contradictions": all_contradictions,
                        "n_papers": len(papers),
                        "n_contradictions": len(all_contradictions)
                    }
                }))
        except Exception as e:
            self.set_status(500)
            self.finish(json.dumps({"status": "error", "message": str(e)}))


# Update setup_route_handlers function to include new routes:

def setup_route_handlers(web_app):
    """Register all API route handlers."""
    host_pattern = ".*$"
    base_url = web_app.settings["base_url"]
    route_prefix = "jupyterlab-research-assistant-wwc-copilot"
    
    handlers = [
        # ... existing handlers ...
        (url_path_join(base_url, route_prefix, "wwc-assessment"), WWCAssessmentHandler),
        (url_path_join(base_url, route_prefix, "meta-analysis"), MetaAnalysisHandler),
        (url_path_join(base_url, route_prefix, "conflict-detection"), ConflictDetectionHandler),
    ]
    
    web_app.add_handlers(host_pattern, handlers)
```

**Manual Testing Checkpoint:**
```bash
# Test WWC assessment endpoint
curl -X POST http://localhost:8888/jupyterlab-research-assistant-wwc-copilot/wwc-assessment \
  -H "Authorization: token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "paper_id": 1,
    "judgments": {
      "chosen_attrition_boundary": "cautious",
      "randomization_documented": true
    }
  }'

# Test meta-analysis endpoint
curl -X POST http://localhost:8888/jupyterlab-research-assistant-wwc-copilot/meta-analysis \
  -H "Authorization: token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "paper_ids": [1, 2, 3],
    "outcome_name": "knowledge_test"
  }'
```

---

## Stage 2: WWC Co-Pilot - Frontend

### Phase 2.6: Update API Client

**Update**: `src/api.ts`

Add these new functions to the existing file:

```typescript
// Add type definitions

export interface IWWCAssessment {
  paper_id?: number;
  paper_title?: string;
  chosen_attrition_boundary: string;
  adjustment_strategy_is_valid?: boolean;
  randomization_documented?: boolean;
  is_rct: boolean;
  overall_attrition?: number;
  differential_attrition?: number;
  is_high_attrition?: boolean;
  baseline_effect_size?: number;
  baseline_equivalence_satisfied?: boolean;
  final_rating: string;
  rating_justification: string[];
}

export interface IWWCAssessmentRequest {
  paper_id: number;
  judgments: {
    chosen_attrition_boundary?: 'cautious' | 'optimistic';
    adjustment_strategy_is_valid?: boolean;
    randomization_documented?: boolean;
  };
}

export interface IMetaAnalysisStudy {
  paper_id?: number;
  study_label: string;
  effect_size: number;
  std_error: number;
  weight: number;
  ci_lower: number;
  ci_upper: number;
}

export interface IMetaAnalysisResult {
  pooled_effect: number;
  ci_lower: number;
  ci_upper: number;
  p_value: number;
  tau_squared: number;
  i_squared: number;
  q_statistic: number;
  q_p_value: number;
  n_studies: number;
  studies: IMetaAnalysisStudy[];
  forest_plot?: string;  // Base64-encoded image
  heterogeneity_interpretation?: string;
}

export interface IConflictDetectionResult {
  contradictions: Array<{
    finding1: string;
    finding2: string;
    confidence: number;
    label: string;
    paper1_id?: number;
    paper1_title?: string;
    paper2_id?: number;
    paper2_title?: string;
  }>;
  n_papers: number;
  n_contradictions: number;
}

// Add API functions

export async function runWWCAssessment(
  request: IWWCAssessmentRequest
): Promise<IWWCAssessment> {
  const response = await requestAPI<IAPIResponse<IWWCAssessment>>(
    'wwc-assessment',
    {
      method: 'POST',
      body: JSON.stringify(request)
    }
  );

  if (response.status === 'error') {
    throw new Error(response.message || 'WWC assessment failed');
  }

  if (!response.data) {
    throw new Error('No assessment data returned');
  }

  return response.data;
}

export async function performMetaAnalysis(
  paperIds: number[],
  outcomeName?: string
): Promise<IMetaAnalysisResult> {
  const response = await requestAPI<IAPIResponse<IMetaAnalysisResult>>(
    'meta-analysis',
    {
      method: 'POST',
      body: JSON.stringify({
        paper_ids: paperIds,
        outcome_name: outcomeName
      })
    }
  );

  if (response.status === 'error') {
    throw new Error(response.message || 'Meta-analysis failed');
  }

  if (!response.data) {
    throw new Error('No meta-analysis data returned');
  }

  return response.data;
}

export async function detectConflicts(
  paperIds: number[],
  confidenceThreshold: number = 0.8
): Promise<IConflictDetectionResult> {
  const response = await requestAPI<IAPIResponse<IConflictDetectionResult>>(
    'conflict-detection',
    {
      method: 'POST',
      body: JSON.stringify({
        paper_ids: paperIds,
        confidence_threshold: confidenceThreshold
      })
    }
  );

  if (response.status === 'error') {
    throw new Error(response.message || 'Conflict detection failed');
  }

  if (!response.data) {
    throw new Error('No conflict detection data returned');
  }

  return response.data;
}
```

### Phase 2.7: Update Library Tab for Multi-Select

**Update**: `src/widgets/LibraryTab.tsx`

Add multi-select functionality:

```typescript
// Add to imports
import { useState } from 'react';

// Add state for selected papers
const [selectedPapers, setSelectedPapers] = useState<Set<number>>(new Set());

// Add selection handler
const handleToggleSelection = (paperId: number) => {
  const newSelection = new Set(selectedPapers);
  if (newSelection.has(paperId)) {
    newSelection.delete(paperId);
  } else {
    newSelection.add(paperId);
  }
  setSelectedPapers(newSelection);
};

// Add "Synthesize Studies" button (show when 2+ papers selected)
{selectedPapers.size >= 2 && (
  <button
    onClick={() => {
      // Open synthesis workbench
      // This will be implemented in Phase 2.8
      console.log('Opening synthesis workbench with papers:', Array.from(selectedPapers));
    }}
    className="jp-jupyterlab-research-assistant-wwc-copilot-button"
  >
    Synthesize {selectedPapers.size} Studies
  </button>
)}

// Update PaperCard to include checkbox
<PaperCard
  key={paper.id}
  paper={paper}
  selected={selectedPapers.has(paper.id || 0)}
  onToggleSelection={() => handleToggleSelection(paper.id || 0)}
/>
```

**Update**: `src/widgets/PaperCard.tsx`

Add checkbox for selection:

```typescript
interface PaperCardProps {
  paper: IPaper;
  onImport?: () => void;
  selected?: boolean;  // NEW
  onToggleSelection?: () => void;  // NEW
}

export const PaperCard: React.FC<PaperCardProps> = ({
  paper,
  onImport,
  selected = false,
  onToggleSelection
}) => {
  return (
    <div className="jp-jupyterlab-research-assistant-wwc-copilot-paper-card">
      {onToggleSelection && (
        <input
          type="checkbox"
          checked={selected}
          onChange={onToggleSelection}
          className="jp-jupyterlab-research-assistant-wwc-copilot-checkbox"
        />
      )}
      <h3>{paper.title}</h3>
      {/* ... rest of component ... */}
    </div>
  );
};
```

### Phase 2.8: WWC Co-Pilot Widget

**File**: `src/widgets/WWCCoPilot.tsx`

```typescript
import React, { useState, useEffect } from 'react';
import { runWWCAssessment, IWWCAssessment, IWWCAssessmentRequest } from '../api';
import { showErrorMessage, showSuccessMessage } from '@jupyterlab/apputils';

interface WWCCoPilotProps {
  paperId: number;
  paperTitle: string;
  onClose?: () => void;
}

export const WWCCoPilot: React.FC<WWCCoPilotProps> = ({
  paperId,
  paperTitle,
  onClose
}) => {
  const [assessment, setAssessment] = useState<IWWCAssessment | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [judgments, setJudgments] = useState<IWWCAssessmentRequest['judgments']>({
    chosen_attrition_boundary: 'cautious',
    adjustment_strategy_is_valid: undefined,
    randomization_documented: undefined
  });

  useEffect(() => {
    runAssessment();
  }, [paperId, judgments]);

  const runAssessment = async () => {
    setIsLoading(true);
    try {
      const request: IWWCAssessmentRequest = {
        paper_id: paperId,
        judgments
      };
      const result = await runWWCAssessment(request);
      setAssessment(result);
    } catch (err) {
      showErrorMessage('WWC Assessment Error', err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setIsLoading(false);
    }
  };

  const getRatingColor = (rating: string) => {
    if (rating.includes('Without Reservations')) return '#4caf50'; // Green
    if (rating.includes('With Reservations')) return '#ff9800'; // Orange
    return '#f44336'; // Red
  };

  return (
    <div className="jp-jupyterlab-research-assistant-wwc-copilot-wwc">
      <div className="jp-jupyterlab-research-assistant-wwc-copilot-wwc-header">
        <h2>WWC Co-Pilot: {paperTitle}</h2>
        {onClose && (
          <button onClick={onClose} className="jp-jupyterlab-research-assistant-wwc-copilot-close">
            ×
          </button>
        )}
      </div>

      {isLoading && <div>Running assessment...</div>}

      {assessment && (
        <>
          {/* User Judgment Section */}
          <div className="jp-jupyterlab-research-assistant-wwc-copilot-wwc-judgments">
            <h3>Your Judgments</h3>
            
            <div className="jp-jupyterlab-research-assistant-wwc-copilot-wwc-field">
              <label>Attrition Boundary:</label>
              <select
                value={judgments.chosen_attrition_boundary || 'cautious'}
                onChange={(e) => setJudgments({
                  ...judgments,
                  chosen_attrition_boundary: e.target.value as 'cautious' | 'optimistic'
                })}
              >
                <option value="cautious">Cautious (default)</option>
                <option value="optimistic">Optimistic</option>
              </select>
              <p className="jp-jupyterlab-research-assistant-wwc-copilot-wwc-help">
                Choose based on whether the intervention could affect who stays in the study.
              </p>
            </div>

            <div className="jp-jupyterlab-research-assistant-wwc-copilot-wwc-field">
              <label>Randomization Documented:</label>
              <select
                value={judgments.randomization_documented === undefined ? '' : String(judgments.randomization_documented)}
                onChange={(e) => setJudgments({
                  ...judgments,
                  randomization_documented: e.target.value === '' ? undefined : e.target.value === 'true'
                })}
              >
                <option value="">Not specified</option>
                <option value="true">Yes</option>
                <option value="false">No</option>
              </select>
            </div>

            <div className="jp-jupyterlab-research-assistant-wwc-copilot-wwc-field">
              <label>Statistical Adjustment Valid:</label>
              <select
                value={judgments.adjustment_strategy_is_valid === undefined ? '' : String(judgments.adjustment_strategy_is_valid)}
                onChange={(e) => setJudgments({
                  ...judgments,
                  adjustment_strategy_is_valid: e.target.value === '' ? undefined : e.target.value === 'true'
                })}
              >
                <option value="">Not applicable</option>
                <option value="true">Yes</option>
                <option value="false">No</option>
              </select>
            </div>
          </div>

          {/* Assessment Results */}
          <div className="jp-jupyterlab-research-assistant-wwc-copilot-wwc-results">
            <h3>Assessment Results</h3>

            {/* Final Rating */}
            <div
              className="jp-jupyterlab-research-assistant-wwc-copilot-wwc-rating"
              style={{ backgroundColor: getRatingColor(assessment.final_rating) }}
            >
              <strong>Final Rating: {assessment.final_rating}</strong>
            </div>

            {/* Attrition Section */}
            {assessment.overall_attrition !== undefined && (
              <div className="jp-jupyterlab-research-assistant-wwc-copilot-wwc-section">
                <h4>Attrition</h4>
                <p>Overall: {(assessment.overall_attrition * 100).toFixed(1)}%</p>
                {assessment.differential_attrition !== undefined && (
                  <p>Differential: {(assessment.differential_attrition * 100).toFixed(1)}%</p>
                )}
                {assessment.is_high_attrition !== undefined && (
                  <p>
                    Status: <strong>{assessment.is_high_attrition ? 'High Attrition' : 'Low Attrition'}</strong>
                  </p>
                )}
              </div>
            )}

            {/* Baseline Equivalence Section */}
            {assessment.baseline_effect_size !== undefined && (
              <div className="jp-jupyterlab-research-assistant-wwc-copilot-wwc-section">
                <h4>Baseline Equivalence</h4>
                <p>Effect Size (Cohen's d): {assessment.baseline_effect_size.toFixed(3)}</p>
                {assessment.baseline_equivalence_satisfied !== undefined && (
                  <p>
                    Status: <strong>
                      {assessment.baseline_equivalence_satisfied ? 'Satisfied' : 'Not Satisfied'}
                    </strong>
                  </p>
                )}
              </div>
            )}

            {/* Justification */}
            <div className="jp-jupyterlab-research-assistant-wwc-copilot-wwc-justification">
              <h4>Justification</h4>
              <ul>
                {assessment.rating_justification.map((reason, idx) => (
                  <li key={idx}>{reason}</li>
                ))}
              </ul>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
```

### Phase 2.9: Synthesis Workbench Widget

**File**: `src/widgets/SynthesisWorkbench.tsx`

```typescript
import React, { useState } from 'react';
import { ReactWidget } from '@jupyterlab/apputils';
import { performMetaAnalysis, detectConflicts, IMetaAnalysisResult, IConflictDetectionResult } from '../api';
import { MetaAnalysisView } from './MetaAnalysisView';
import { ConflictView } from './ConflictView';
import { showErrorMessage } from '@jupyterlab/apputils';

interface SynthesisWorkbenchProps {
  paperIds: number[];
  onClose?: () => void;
}

const SynthesisWorkbenchComponent: React.FC<SynthesisWorkbenchProps> = ({
  paperIds,
  onClose
}) => {
  const [activeTab, setActiveTab] = useState<'meta-analysis' | 'conflicts'>('meta-analysis');
  const [metaAnalysisResult, setMetaAnalysisResult] = useState<IMetaAnalysisResult | null>(null);
  const [conflictResult, setConflictResult] = useState<IConflictDetectionResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleRunMetaAnalysis = async () => {
    setIsLoading(true);
    try {
      const result = await performMetaAnalysis(paperIds);
      setMetaAnalysisResult(result);
      setActiveTab('meta-analysis');
    } catch (err) {
      showErrorMessage('Meta-Analysis Error', err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDetectConflicts = async () => {
    setIsLoading(true);
    try {
      const result = await detectConflicts(paperIds);
      setConflictResult(result);
      setActiveTab('conflicts');
    } catch (err) {
      showErrorMessage('Conflict Detection Error', err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="jp-jupyterlab-research-assistant-wwc-copilot-synthesis">
      <div className="jp-jupyterlab-research-assistant-wwc-copilot-synthesis-header">
        <h2>Synthesis Workbench ({paperIds.length} studies)</h2>
        {onClose && (
          <button onClick={onClose} className="jp-jupyterlab-research-assistant-wwc-copilot-close">
            ×
          </button>
        )}
      </div>

      <div className="jp-jupyterlab-research-assistant-wwc-copilot-synthesis-actions">
        <button
          onClick={handleRunMetaAnalysis}
          disabled={isLoading}
          className="jp-jupyterlab-research-assistant-wwc-copilot-button"
        >
          Run Meta-Analysis
        </button>
        <button
          onClick={handleDetectConflicts}
          disabled={isLoading}
          className="jp-jupyterlab-research-assistant-wwc-copilot-button"
        >
          Detect Conflicts
        </button>
      </div>

      {isLoading && <div>Processing...</div>}

      <div className="jp-jupyterlab-research-assistant-wwc-copilot-synthesis-tabs">
        <button
          className={activeTab === 'meta-analysis' ? 'active' : ''}
          onClick={() => setActiveTab('meta-analysis')}
        >
          Meta-Analysis
        </button>
        <button
          className={activeTab === 'conflicts' ? 'active' : ''}
          onClick={() => setActiveTab('conflicts')}
        >
          Conflicts ({conflictResult?.n_contradictions || 0})
        </button>
      </div>

      <div className="jp-jupyterlab-research-assistant-wwc-copilot-synthesis-content">
        {activeTab === 'meta-analysis' && metaAnalysisResult && (
          <MetaAnalysisView result={metaAnalysisResult} />
        )}
        {activeTab === 'conflicts' && conflictResult && (
          <ConflictView result={conflictResult} />
        )}
        {!metaAnalysisResult && !conflictResult && (
          <div>Click "Run Meta-Analysis" or "Detect Conflicts" to begin.</div>
        )}
      </div>
    </div>
  );
};

export class SynthesisWorkbench extends ReactWidget {
  private paperIds: number[];

  constructor(paperIds: number[]) {
    super();
    this.paperIds = paperIds;
    this.addClass('jp-jupyterlab-research-assistant-wwc-copilot-synthesis-widget');
    this.id = 'synthesis-workbench';
    this.title.label = 'Synthesis Workbench';
    this.title.caption = 'Meta-Analysis & Conflict Detection';
    this.title.closable = true;
  }

  render(): JSX.Element {
    return <SynthesisWorkbenchComponent paperIds={this.paperIds} />;
  }
}
```

### Phase 2.10: Meta-Analysis View Component

**File**: `src/widgets/MetaAnalysisView.tsx`

```typescript
import React from 'react';
import { IMetaAnalysisResult } from '../api';

interface MetaAnalysisViewProps {
  result: IMetaAnalysisResult;
}

export const MetaAnalysisView: React.FC<MetaAnalysisViewProps> = ({ result }) => {
  return (
    <div className="jp-jupyterlab-research-assistant-wwc-copilot-meta-analysis">
      <h3>Meta-Analysis Results</h3>

      {/* Summary Statistics */}
      <div className="jp-jupyterlab-research-assistant-wwc-copilot-meta-analysis-summary">
        <div className="jp-jupyterlab-research-assistant-wwc-copilot-meta-analysis-stat">
          <strong>Pooled Effect Size:</strong>
          <span>d = {result.pooled_effect.toFixed(3)}</span>
        </div>
        <div className="jp-jupyterlab-research-assistant-wwc-copilot-meta-analysis-stat">
          <strong>95% Confidence Interval:</strong>
          <span>[{result.ci_lower.toFixed(3)}, {result.ci_upper.toFixed(3)}]</span>
        </div>
        <div className="jp-jupyterlab-research-assistant-wwc-copilot-meta-analysis-stat">
          <strong>P-value:</strong>
          <span>{result.p_value.toFixed(4)}</span>
        </div>
        <div className="jp-jupyterlab-research-assistant-wwc-copilot-meta-analysis-stat">
          <strong>I² (Heterogeneity):</strong>
          <span>{result.i_squared.toFixed(1)}% - {result.heterogeneity_interpretation}</span>
        </div>
        <div className="jp-jupyterlab-research-assistant-wwc-copilot-meta-analysis-stat">
          <strong>Number of Studies:</strong>
          <span>{result.n_studies}</span>
        </div>
      </div>

      {/* Forest Plot */}
      {result.forest_plot && (
        <div className="jp-jupyterlab-research-assistant-wwc-copilot-meta-analysis-plot">
          <h4>Forest Plot</h4>
          <img
            src={`data:image/png;base64,${result.forest_plot}`}
            alt="Forest Plot"
            style={{ maxWidth: '100%', height: 'auto' }}
          />
        </div>
      )}

      {/* Individual Study Results */}
      <div className="jp-jupyterlab-research-assistant-wwc-copilot-meta-analysis-studies">
        <h4>Individual Studies</h4>
        <table className="jp-jupyterlab-research-assistant-wwc-copilot-table">
          <thead>
            <tr>
              <th>Study</th>
              <th>Effect Size</th>
              <th>95% CI</th>
              <th>Weight</th>
            </tr>
          </thead>
          <tbody>
            {result.studies.map((study, idx) => (
              <tr key={idx}>
                <td>{study.study_label}</td>
                <td>{study.effect_size.toFixed(3)}</td>
                <td>[{study.ci_lower.toFixed(3)}, {study.ci_upper.toFixed(3)}]</td>
                <td>{(study.weight * 100).toFixed(1)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
```

### Phase 2.11: Conflict View Component

**File**: `src/widgets/ConflictView.tsx`

```typescript
import React from 'react';
import { IConflictDetectionResult } from '../api';

interface ConflictViewProps {
  result: IConflictDetectionResult;
}

export const ConflictView: React.FC<ConflictViewProps> = ({ result }) => {
  return (
    <div className="jp-jupyterlab-research-assistant-wwc-copilot-conflicts">
      <h3>Conflict Detection Results</h3>

      <div className="jp-jupyterlab-research-assistant-wwc-copilot-conflicts-summary">
        <p>
          Found <strong>{result.n_contradictions}</strong> contradictions across{' '}
          <strong>{result.n_papers}</strong> papers.
        </p>
      </div>

      {result.contradictions.length === 0 ? (
        <div>No contradictions detected.</div>
      ) : (
        <div className="jp-jupyterlab-research-assistant-wwc-copilot-conflicts-list">
          {result.contradictions.map((conflict, idx) => (
            <div key={idx} className="jp-jupyterlab-research-assistant-wwc-copilot-conflict-item">
              <div className="jp-jupyterlab-research-assistant-wwc-copilot-conflict-header">
                <strong>Contradiction #{idx + 1}</strong>
                <span>Confidence: {(conflict.confidence * 100).toFixed(1)}%</span>
              </div>
              {conflict.paper1_title && conflict.paper2_title && (
                <div className="jp-jupyterlab-research-assistant-wwc-copilot-conflict-papers">
                  <div>
                    <strong>Paper 1:</strong> {conflict.paper1_title}
                  </div>
                  <div>
                    <strong>Paper 2:</strong> {conflict.paper2_title}
                  </div>
                </div>
              )}
              <div className="jp-jupyterlab-research-assistant-wwc-copilot-conflict-findings">
                <div>
                  <strong>Finding 1:</strong> {conflict.finding1}
                </div>
                <div>
                  <strong>Finding 2:</strong> {conflict.finding2}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
```

### Phase 2.12: Integrate into Main Plugin

**Update**: `src/index.ts`

Add commands and widget registration:

```typescript
// Add to imports
import { SynthesisWorkbench } from './widgets/SynthesisWorkbench';
import { WWCCoPilot } from './widgets/WWCCoPilot';

// Add commands in activate function
app.commands.addCommand('jupyterlab-research-assistant-wwc-copilot:open-synthesis', {
  label: 'Open Synthesis Workbench',
  execute: (args: any) => {
    const paperIds = args.paperIds as number[] || [];
    if (paperIds.length < 2) {
      showErrorMessage('Synthesis Workbench', 'Please select at least 2 papers');
      return;
    }
    const workbench = new SynthesisWorkbench(paperIds);
    app.shell.add(workbench, 'main');
    app.shell.activateById(workbench.id);
  }
});

app.commands.addCommand('jupyterlab-research-assistant-wwc-copilot:open-wwc', {
  label: 'Open WWC Co-Pilot',
  execute: (args: any) => {
    const paperId = args.paperId as number;
    const paperTitle = args.paperTitle as string || 'Paper';
    // Create a widget for WWC assessment
    // Implementation depends on whether you want it as a main area widget or dialog
    // For now, we'll show it in a dialog
    showDialog({
      title: `WWC Co-Pilot: ${paperTitle}`,
      body: ReactWidget.create(<WWCCoPilot paperId={paperId} paperTitle={paperTitle} />),
      buttons: [Dialog.okButton()]
    });
  }
});

// Update LibraryTab to call synthesis command
// In LibraryTab.tsx, update the "Synthesize Studies" button:
app.commands.execute('jupyterlab-research-assistant-wwc-copilot:open-synthesis', {
  paperIds: Array.from(selectedPapers)
});
```

---

## Testing Checkpoints

### After Each Backend Feature

1. **Unit Test**: Write a simple test in a Jupyter notebook
2. **API Test**: Use curl or browser dev tools to test endpoint
3. **Error Handling**: Test with invalid inputs
4. **Edge Cases**: Test with missing data, boundary conditions

### After Each Frontend Feature

1. **Visual Check**: Does it render correctly?
2. **Interaction**: Do buttons/inputs work?
3. **Console**: Check browser console for errors
4. **Network**: Check Network tab for API calls
5. **State**: Does state update correctly?

### Integration Testing

1. **Full Workflow**: Select papers → Run WWC assessment → Run meta-analysis → View results
2. **Error Scenarios**: Test with network errors, invalid data, insufficient studies
3. **Edge Cases**: Single study, missing effect sizes, incomplete data

---

## Common Issues & Solutions

### Issue: Meta-Analysis Fails with "Insufficient studies"

**Solution:**
- Verify papers have effect size data in `study_metadata.effect_sizes`
- Check that `outcome_name` matches a key in effect_sizes
- Ensure at least 2 papers have the same outcome measure

### Issue: Forest Plot Not Displaying

**Solution:**
1. Check browser console for base64 decode errors
2. Verify backend returns `forest_plot` field in response
3. Check image format (should be PNG base64)
4. Verify img tag src format: `data:image/png;base64,${result.forest_plot}`

### Issue: WWC Assessment Returns "Insufficient data"

**Solution:**
- Ensure paper has `sample_size_baseline` and `sample_size_endline` in database
- Or provide `treatment_attrition` and `control_attrition` rates
- Check that `methodology` field is set correctly

### Issue: Conflict Detection Not Working

**Solution:**
- Verify `transformers` library is installed
- Check that papers have `full_text` or `abstract` in database
- Reduce `confidence_threshold` if no conflicts found
- Check server logs for NLI model loading errors

### Issue: Statsmodels Import Error

**Solution:**
```bash
pip install statsmodels numpy scipy
```

### Issue: Matplotlib Backend Error

**Solution:**
- Ensure `matplotlib.use('Agg')` is called before importing pyplot
- This sets non-interactive backend for server use

---

## Next Steps

After completing Stage 2 Core Features:

### Remaining Stage 2 Enhancements

1. **Enhanced WWC UI**: Multi-step wizard, progress indicators, save/load assessments
2. **Subgroup Analysis**: Meta-analysis by moderator variables (e.g., age group, intervention type)
3. **Publication Bias Assessment**: Funnel plots, Egger's test
4. **Export Reports**: Generate Markdown/PDF synthesis reports
5. **Advanced Conflict Detection**: Use AI extraction for better finding identification
6. **Sensitivity Analysis**: Leave-one-out analysis, influence diagnostics

### Stage 3: Finalization & Documentation

After completing Stage 2, proceed to Stage 3 (see `docs/master-plan.md` for details):
- Comprehensive testing
- User documentation
- Developer documentation
- Community submission preparation

