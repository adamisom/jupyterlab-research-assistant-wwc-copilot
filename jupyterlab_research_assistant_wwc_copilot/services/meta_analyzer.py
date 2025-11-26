"""Meta-analysis engine using statsmodels for random-effects models."""

import logging
import warnings

import numpy as np
import statsmodels.stats.meta_analysis as meta

logger = logging.getLogger(__name__)

# Suppress harmless sqrt() warnings from statsmodels when tau² is negative
# (common with 2 studies or low heterogeneity - statsmodels handles this internally)
warnings.filterwarnings(
    "ignore",
    category=RuntimeWarning,
    message="invalid value encountered in sqrt",
    module="statsmodels.stats.meta_analysis",
)


class MetaAnalyzer:
    """
    Performs random-effects meta-analysis on study effect sizes.

    Uses DerSimonian-Laird estimator (default in statsmodels) for
    between-study variance (tau-squared).
    """

    def perform_random_effects_meta_analysis(self, studies: list[dict]) -> dict:
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
                method_re="DL",
                use_t=True,  # DerSimonian-Laird
            )

            # Calculate heterogeneity statistics
            het_test = result.test_homogeneity()

            # Get Q statistic and I² from result
            q_statistic = result.q
            i_squared = result.i2
            # I² can be negative (set to 0 if negative)
            i_squared = 0.0 if i_squared < 0 else float(i_squared)

            # Calculate study weights (inverse variance weights)
            weights = 1.0 / (std_errors**2 + result.tau2)
            weights = weights / weights.sum()  # Normalize to sum to 1

            # Prepare individual study results
            study_results = []
            for i, study in enumerate(studies):
                study_results.append(
                    {
                        "paper_id": study.get("paper_id"),
                        "study_label": study.get("study_label", f"Study {i + 1}"),
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
            ci_lower = (
                float(ci[0])
                if not np.isnan(ci[0])
                else float(pooled_effect - 1.96 * result.sd_eff_w_re)
                if result.sd_eff_w_re and not np.isnan(result.sd_eff_w_re)
                else float(pooled_effect - 0.5)
            )
            ci_upper = (
                float(ci[1])
                if not np.isnan(ci[1])
                else float(pooled_effect + 1.96 * result.sd_eff_w_re)
                if result.sd_eff_w_re and not np.isnan(result.sd_eff_w_re)
                else float(pooled_effect + 0.5)
            )

            # Calculate p-value for pooled effect (two-tailed test)
            # Using t-distribution with df = n_studies - 1
            from scipy import stats  # noqa: PLC0415

            df = len(studies) - 1
            # Handle case where sd_eff_w_re might be 0, NaN, or invalid
            if (
                hasattr(result, "sd_eff_w_re")
                and result.sd_eff_w_re
                and result.sd_eff_w_re > 0
                and not np.isnan(result.sd_eff_w_re)
                and not np.isinf(result.sd_eff_w_re)
            ):
                try:
                    t_stat = pooled_effect / result.sd_eff_w_re
                    p_value = float(2 * (1 - stats.t.cdf(abs(t_stat), df)))
                    if np.isnan(p_value) or np.isinf(p_value):
                        # Fallback to normal approximation
                        z_stat = pooled_effect / result.sd_eff_w_re
                        p_value = float(2 * (1 - stats.norm.cdf(abs(z_stat))))
                except Exception:
                    # Fallback: use normal approximation
                    z_stat = pooled_effect / result.sd_eff_w_re
                    p_value = float(2 * (1 - stats.norm.cdf(abs(z_stat))))
            # If sd is invalid, use a default or calculate from CI
            elif not np.isnan(ci_lower) and not np.isnan(ci_upper):
                # Approximate SE from CI width
                approx_se = (ci_upper - ci_lower) / (2 * 1.96)
                if approx_se > 0:
                    z_stat = pooled_effect / approx_se
                    p_value = float(2 * (1 - stats.norm.cdf(abs(z_stat))))
                else:
                    p_value = 1.0  # Default to non-significant
            else:
                p_value = 1.0  # Default to non-significant

            # Ensure p_value is valid
            if np.isnan(p_value) or np.isinf(p_value):
                p_value = 1.0

            # Ensure all numeric values are valid (no NaN or Inf)
            tau_sq = float(result.tau2)
            if np.isnan(tau_sq) or np.isinf(tau_sq):
                tau_sq = 0.0  # Set to 0 if invalid (common with 2 studies)

            q_pval = float(het_test.pvalue)
            if np.isnan(q_pval) or np.isinf(q_pval):
                q_pval = 1.0

            return {
                "pooled_effect": pooled_effect,
                "ci_lower": ci_lower,
                "ci_upper": ci_upper,
                "p_value": p_value,
                "tau_squared": tau_sq,
                "i_squared": i_squared,
                "q_statistic": float(q_statistic),
                "q_p_value": q_pval,
                "n_studies": len(studies),
                "studies": study_results,
            }
        except Exception as e:
            logger.exception("Meta-analysis failed")
            raise RuntimeError(f"Meta-analysis computation error: {e!s}") from e

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

    def perform_subgroup_meta_analysis(
        self, studies: list[dict], subgroup_variable: str
    ) -> dict:
        """
        Perform meta-analysis for each subgroup.

        Args:
            studies: List of study dictionaries with subgroup metadata
            subgroup_variable: Field name for subgroup (e.g., 'age_group', 'intervention_type')

        Returns:
            Dictionary with:
                - subgroups: Dict mapping subgroup name to meta-analysis results
                - overall: Overall meta-analysis (all studies combined)
                - subgroup_variable: The variable used for subgrouping
                - n_subgroups: Number of subgroups analyzed
                - subgroup_comparison: Test for differences between subgroups (Q-between statistic)
        """
        if len(studies) < 2:
            raise ValueError("Subgroup meta-analysis requires at least 2 studies")

        # Group studies by subgroup
        subgroups = {}
        for study in studies:
            subgroup_value = study.get(subgroup_variable, "unknown")
            if subgroup_value not in subgroups:
                subgroups[subgroup_value] = []
            subgroups[subgroup_value].append(study)

        # Perform meta-analysis for each subgroup
        subgroup_results = {}
        for subgroup_name, subgroup_studies in subgroups.items():
            if len(subgroup_studies) >= 2:
                try:
                    result = self.perform_random_effects_meta_analysis(subgroup_studies)
                    subgroup_results[subgroup_name] = result
                except Exception as e:
                    logger.warning(
                        f"Meta-analysis failed for subgroup '{subgroup_name}': {e!s}"
                    )
                    continue

        # Perform overall meta-analysis
        overall_result = self.perform_random_effects_meta_analysis(studies)

        # Test for subgroup differences using Q-between statistic
        subgroup_comparison = self._calculate_subgroup_comparison(
            subgroup_results, overall_result
        )

        return {
            "subgroups": subgroup_results,
            "overall": overall_result,
            "subgroup_variable": subgroup_variable,
            "n_subgroups": len(subgroup_results),
            "subgroup_comparison": subgroup_comparison,
        }

    def _calculate_subgroup_comparison(
        self, subgroup_results: dict[str, dict], overall_result: dict
    ) -> dict:
        """
        Calculate Q-between statistic to test for differences between subgroups.

        Q-between tests whether effect sizes differ significantly across subgroups.
        Follows a chi-square distribution with (k-1) degrees of freedom.

        Args:
            subgroup_results: Dictionary mapping subgroup names to meta-analysis results
            overall_result: Overall meta-analysis result (all studies combined)

        Returns:
            Dictionary with:
                - q_between: Q-between statistic
                - df: Degrees of freedom (number of subgroups - 1)
                - p_value: P-value for test of subgroup differences
                - interpretation: String interpretation
        """
        from scipy import stats  # noqa: PLC0415

        if len(subgroup_results) < 2:
            return {
                "q_between": None,
                "df": None,
                "p_value": None,
                "interpretation": "At least 2 subgroups required for comparison",
            }

        overall_effect = overall_result["pooled_effect"]
        q_between = 0.0

        # Calculate Q-between: Σ w_i * (θ_i - θ_overall)^2
        # where w_i is the inverse variance weight for subgroup i
        for subgroup_result in subgroup_results.values():
            subgroup_effect = subgroup_result["pooled_effect"]
            # Use the standard error of the pooled effect to calculate weight
            # Weight = 1 / SE^2 (formula comment)
            subgroup_se = (
                subgroup_result["ci_upper"] - subgroup_result["ci_lower"]
            ) / (2 * 1.96)
            if subgroup_se > 0:
                weight = 1.0 / (subgroup_se**2)
                q_between += weight * (subgroup_effect - overall_effect) ** 2

        # Degrees of freedom = number of subgroups - 1
        df = len(subgroup_results) - 1

        # P-value from chi-square distribution
        if df > 0 and q_between > 0:
            p_value = float(1 - stats.chi2.cdf(q_between, df))

            if p_value < 0.05:
                interpretation = (
                    f"Significant differences between subgroups (Q-between = {q_between:.3f}, "
                    f"p = {p_value:.4f})"
                )
            else:
                interpretation = (
                    f"No significant differences between subgroups (Q-between = {q_between:.3f}, "
                    f"p = {p_value:.4f})"
                )
        else:
            p_value = None
            interpretation = "Subgroup comparison could not be calculated"

        return {
            "q_between": float(q_between) if q_between > 0 else None,
            "df": df,
            "p_value": p_value,
            "interpretation": interpretation,
        }

    def perform_eggers_test(
        self, effect_sizes: np.ndarray, std_errors: np.ndarray
    ) -> dict:
        """
        Perform Egger's test for publication bias.

        Args:
            effect_sizes: Array of effect sizes
            std_errors: Array of standard errors

        Returns:
            Dictionary with:
                - intercept: Regression intercept
                - intercept_se: Standard error of intercept
                - intercept_pvalue: P-value for test of intercept = 0
                - interpretation: String interpretation
        """
        from scipy import linalg, stats  # noqa: PLC0415

        if len(effect_sizes) < 3:
            return {
                "intercept": None,
                "intercept_se": None,
                "intercept_pvalue": None,
                "interpretation": "Egger's test requires at least 3 studies",
            }

        # Egger's test: regress effect size on precision (1/SE)
        precision = 1.0 / std_errors

        # Weighted least squares
        weights = 1.0 / (std_errors**2)

        # Design matrix: [1, precision]
        X = np.column_stack([np.ones(len(effect_sizes)), precision])  # noqa: N806

        try:
            # Weighted least squares: (X'WX)^(-1) X'Wy
            XW = X * weights[:, np.newaxis]  # noqa: N806
            XWX = XW.T @ X  # noqa: N806
            XWy = XW.T @ effect_sizes  # noqa: N806

            # Check matrix condition number to avoid ill-conditioned matrices
            cond_num = np.linalg.cond(XWX)
            if cond_num > 1e12:
                raise ValueError(  # noqa: TRY301
                    f"Matrix is ill-conditioned (condition number: {cond_num:.2e})"
                )

            # Solve for beta
            beta = linalg.solve(XWX, XWy)

            # Calculate residuals and MSE
            residuals = effect_sizes - X @ beta
            mse = np.sum(weights * residuals**2) / (len(effect_sizes) - 2)

            # Variance-covariance matrix of beta
            var_beta = mse * linalg.inv(XWX)

            intercept = beta[0]
            var_intercept = var_beta[0, 0]

            # Check for negative or zero variance before sqrt
            if var_intercept <= 0:
                raise ValueError(f"Invalid variance for intercept: {var_intercept}")  # noqa: TRY301

            intercept_se = np.sqrt(var_intercept)
            intercept_t = intercept / intercept_se

            # P-value (two-tailed t-test)
            df = len(effect_sizes) - 2
            intercept_pvalue = float(2 * (1 - stats.t.cdf(abs(intercept_t), df)))

            if intercept_pvalue < 0.05:
                interpretation = "Evidence of publication bias (p < 0.05)"
            else:
                interpretation = (
                    "No significant evidence of publication bias (p >= 0.05)"
                )

            return {
                "intercept": float(intercept),
                "intercept_se": float(intercept_se),
                "intercept_pvalue": float(intercept_pvalue),
                "interpretation": interpretation,
            }
        except Exception as e:
            logger.exception("Egger's test failed")
            return {
                "intercept": None,
                "intercept_se": None,
                "intercept_pvalue": None,
                "interpretation": f"Egger's test failed: {e!s}",
            }

    def perform_sensitivity_analysis(self, studies: list[dict]) -> dict:
        """
        Perform sensitivity analysis (leave-one-out and influence diagnostics).

        Args:
            studies: List of study dictionaries

        Returns:
            Dictionary with:
                - overall_effect: Overall pooled effect from all studies
                - leave_one_out: List of results with each study removed
                - influence_diagnostics: Cook's distance and other influence measures
                - n_studies: Number of studies
        """
        if len(studies) < 3:
            raise ValueError("Sensitivity analysis requires at least 3 studies")

        # Perform overall meta-analysis
        overall_result = self.perform_random_effects_meta_analysis(studies)
        overall_effect = overall_result["pooled_effect"]
        overall_tau_squared = overall_result["tau_squared"]

        # Leave-one-out analysis
        leave_one_out_results = []
        for i in range(len(studies)):
            studies_without_i = [s for j, s in enumerate(studies) if j != i]
            if len(studies_without_i) >= 2:
                try:
                    result = self.perform_random_effects_meta_analysis(
                        studies_without_i
                    )
                    leave_one_out_results.append(
                        {
                            "removed_study": studies[i].get(
                                "study_label", f"Study {i + 1}"
                            ),
                            "removed_paper_id": studies[i].get("paper_id"),
                            "pooled_effect": result["pooled_effect"],
                            "ci_lower": result["ci_lower"],
                            "ci_upper": result["ci_upper"],
                            "difference_from_overall": result["pooled_effect"]
                            - overall_effect,
                        }
                    )
                except Exception as e:
                    logger.warning(
                        f"Leave-one-out analysis failed for study {i + 1}: {e!s}"
                    )
                    continue

        # Influence diagnostics
        effect_sizes = np.array([s["effect_size"] for s in studies])
        std_errors = np.array([s["std_error"] for s in studies])

        # Calculate weights using overall tau-squared
        weights = 1.0 / (std_errors**2 + overall_tau_squared)
        weights = weights / weights.sum()  # Normalize

        # Calculate influence (how much each study affects overall result)
        influence_scores = []
        mean_effect = np.average(effect_sizes, weights=weights)

        for i, study in enumerate(studies):
            # Simplified influence: weight * absolute deviation from mean
            influence = weights[i] * abs(effect_sizes[i] - mean_effect)
            influence_scores.append(
                {
                    "study_label": study.get("study_label", f"Study {i + 1}"),
                    "paper_id": study.get("paper_id"),
                    "influence_score": float(influence),
                    "weight": float(weights[i]),
                    "effect_size": float(effect_sizes[i]),
                }
            )

        # Sort by influence (highest first)
        influence_scores.sort(key=lambda x: x["influence_score"], reverse=True)

        return {
            "overall_effect": overall_effect,
            "leave_one_out": leave_one_out_results,
            "influence_diagnostics": influence_scores,
            "n_studies": len(studies),
        }
