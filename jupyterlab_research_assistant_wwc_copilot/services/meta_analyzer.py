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

    def perform_random_effects_meta_analysis(self, studies: List[Dict]) -> Dict:
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
                effect_sizes, std_errors, method_re="DL", use_t=True  # DerSimonian-Laird
            )

            # Calculate heterogeneity statistics
            het_test = result.test_homogeneity()

            # Get Q statistic and I² from result
            q_statistic = result.q
            i_squared = result.i2
            # I² can be negative (set to 0 if negative)
            if i_squared < 0:
                i_squared = 0.0
            else:
                i_squared = float(i_squared)

            # Calculate study weights (inverse variance weights)
            weights = 1.0 / (std_errors**2 + result.tau2)
            weights = weights / weights.sum()  # Normalize to sum to 1

            # Prepare individual study results
            study_results = []
            for i, study in enumerate(studies):
                study_results.append(
                    {
                        "paper_id": study.get("paper_id"),
                        "study_label": study.get("study_label", f"Study {i+1}"),
                        "effect_size": float(effect_sizes[i]),
                        "std_error": float(std_errors[i]),
                        "weight": float(weights[i]),
                        "ci_lower": float(effect_sizes[i] - 1.96 * std_errors[i]),
                        "ci_upper": float(effect_sizes[i] + 1.96 * std_errors[i]),
                    }
                )

            # Get random-effects pooled effect and confidence interval
            pooled_effect = float(result.mean_effect_re)
            ci = result.conf_int()[2]  # Random-effects CI (index 2)
            ci_lower = float(ci[0])
            ci_upper = float(ci[1])

            # Calculate p-value for pooled effect (two-tailed test)
            # Using t-distribution with df = n_studies - 1
            from scipy import stats

            df = len(studies) - 1
            t_stat = pooled_effect / result.sd_eff_w_re
            p_value = float(2 * (1 - stats.t.cdf(abs(t_stat), df)))

            return {
                "pooled_effect": pooled_effect,
                "ci_lower": ci_lower,
                "ci_upper": ci_upper,
                "p_value": p_value,
                "tau_squared": float(result.tau2),
                "i_squared": i_squared,
                "q_statistic": float(q_statistic),
                "q_p_value": float(het_test.pvalue),
                "n_studies": len(studies),
                "studies": study_results,
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

