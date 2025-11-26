# Meta-Analysis sqrt() Warnings: Common Reasons & Workarounds

## Overview

When running meta-analysis, you may see RuntimeWarnings like:

```
RuntimeWarning: invalid value encountered in sqrt
  sd_eff_w_re = np.sqrt(var_eff_w_re)
```

These warnings occur when `statsmodels` tries to take the square root of negative or invalid variance values during internal calculations. **In most cases, these warnings are harmless** - the library handles them internally and returns valid results.

## Common Reasons

### 1. **Small Number of Studies (Especially N=2)**

**Why it happens:**

- With only 2 studies, the DerSimonian-Laird estimator for tau² (between-study variance) can produce negative values
- Negative tau² is mathematically invalid (variance can't be negative)
- `statsmodels` sets negative tau² to 0, but internal calculations may still use the negative value temporarily

**Example:**

```python
# Two studies with similar effect sizes
studies = [
    {"effect_size": 0.5, "std_error": 0.15},
    {"effect_size": 0.6, "std_error": 0.18}
]
# Low heterogeneity → tau² might be negative → sqrt warning
```

**Workaround:**

- Use **fixed-effects model** when you have only 2 studies (no random-effects variance to estimate)
- Or accept the warning - results are still valid (tau² is set to 0)

### 2. **Very Low Heterogeneity**

**Why it happens:**

- When studies have very similar effect sizes, heterogeneity is low
- Low heterogeneity → small or negative tau² estimate
- The variance calculations (`var_eff_w_re`, `var_hksj_re`) can become negative

**Example:**

```python
# Studies with nearly identical effects
studies = [
    {"effect_size": 0.45, "std_error": 0.12},
    {"effect_size": 0.46, "std_error": 0.13},
    {"effect_size": 0.44, "std_error": 0.11}
]
# Very low Q statistic → negative tau² → sqrt warning
```

**Workaround:**

- This is actually a **good sign** - it means your studies are consistent
- The warning is harmless; results are valid
- Consider using fixed-effects model if heterogeneity is truly zero

### 3. **Very Small Standard Errors**

**Why it happens:**

- Studies with very precise estimates (small SE) can cause numerical instability
- When SEs are very small, variance calculations can become sensitive to rounding errors
- Matrix operations in weighted least squares can become ill-conditioned

**Example:**

```python
# Studies with extremely precise estimates
studies = [
    {"effect_size": 0.5, "std_error": 0.01},  # Very precise
    {"effect_size": 0.6, "std_error": 0.01}   # Very precise
]
# Small SEs → large weights → numerical instability
```

**Workaround:**

- Verify that standard errors are realistic (not artificially small)
- Check for data entry errors (SE should typically be > 0.05 for Cohen's d)
- If SEs are legitimately very small, the warnings are harmless

### 4. **Numerical Precision Issues**

**Why it happens:**

- Floating-point arithmetic can produce values slightly below zero due to rounding
- Matrix inversion in weighted least squares can amplify small errors
- This is especially common with:
  - Many studies (>10)
  - Studies with very different weights
  - Ill-conditioned matrices

**Workaround:**

- Usually harmless - `statsmodels` handles these internally
- Results are still valid

### 5. **Missing or Invalid Data**

**Why it happens:**

- If effect sizes or standard errors contain NaN, Inf, or invalid values
- If standard errors are zero or negative (should be caught by validation)

**Example:**

```python
# Invalid data (should be caught by validation)
studies = [
    {"effect_size": 0.5, "std_error": 0.0},  # Invalid: SE = 0
    {"effect_size": 0.6, "std_error": -0.1}  # Invalid: negative SE
]
```

**Workaround:**

- Our code validates inputs (checks `std_errors > 0`)
- Ensure data quality before running meta-analysis

## Workarounds

### 1. **Suppress Warnings (Recommended for Production)**

If warnings are harmless but noisy, suppress them:

```python
import warnings
import numpy as np

# Suppress only sqrt warnings from statsmodels
warnings.filterwarnings(
    'ignore',
    category=RuntimeWarning,
    message='invalid value encountered in sqrt',
    module='statsmodels.stats.meta_analysis'
)
```

**Note:** Only suppress if you've verified the warnings are harmless (results are valid).

### 2. **Use Fixed-Effects Model for Small N**

For 2-3 studies, consider using fixed-effects instead of random-effects:

```python
# Fixed-effects (no tau² estimation)
result = meta.combine_effects(
    effect_sizes,
    std_errors,
    method_re=None,  # No random effects
    use_t=True
)
```

**Trade-off:** Fixed-effects assumes all studies share the same true effect (no heterogeneity).

### 3. **Validate Data Quality**

Before running meta-analysis, validate:

```python
# Check for invalid values
if np.any(std_errors <= 0):
    raise ValueError("Standard errors must be positive")

if np.any(np.isnan(effect_sizes)) or np.any(np.isnan(std_errors)):
    raise ValueError("Effect sizes and standard errors cannot be NaN")

if np.any(np.isinf(effect_sizes)) or np.any(np.isinf(std_errors)):
    raise ValueError("Effect sizes and standard errors cannot be infinite")

# Check for unrealistic values
if np.any(std_errors < 0.01):
    logger.warning("Very small standard errors detected - may cause numerical issues")
```

### 4. **Handle Negative Tau² Explicitly**

Our code already handles this:

```python
tau_sq = float(result.tau2)
if np.isnan(tau_sq) or np.isinf(tau_sq) or tau_sq < 0:
    tau_sq = 0.0  # Set to 0 if invalid
```

This ensures tau² is never negative in our calculations.

### 5. **Use Alternative Estimators**

If DerSimonian-Laird (DL) produces warnings, try other estimators:

```python
# Restricted Maximum Likelihood (REML)
result = meta.combine_effects(
    effect_sizes,
    std_errors,
    method_re="REML",  # Alternative estimator
    use_t=True
)

# Or Hedges-Vevea estimator
result = meta.combine_effects(
    effect_sizes,
    std_errors,
    method_re="HE",  # Hedges-Vevea
    use_t=True
)
```

**Note:** Different estimators may give slightly different results.

## When to Worry

**These warnings are usually harmless if:**

- ✅ Results look reasonable (pooled effect, CI, p-value are valid)
- ✅ No NaN or Inf values in final results
- ✅ You have at least 2 studies
- ✅ Standard errors are positive and reasonable

**Investigate further if:**

- ❌ Final results contain NaN or Inf
- ❌ Confidence intervals are invalid (lower > upper)
- ❌ P-values are NaN or outside [0, 1]
- ❌ You have only 1 study (meta-analysis requires ≥2)
- ❌ Standard errors are zero or negative (should be caught by validation)

## Current Implementation

Our `MetaAnalyzer` class already handles many edge cases:

1. **Validates inputs:** Checks that standard errors are positive
2. **Handles invalid tau²:** Sets negative/NaN tau² to 0
3. **Validates outputs:** Checks for NaN/Inf in final results
4. **Fallback calculations:** Uses alternative methods if primary calculation fails

The warnings you see are from **inside statsmodels** before our code can catch them. The library handles them internally and returns valid results.

## Recommended Action

**For now:** These warnings are harmless and can be safely ignored. The meta-analysis results are still valid.

**Future improvement:** Add warning suppression in `meta_analyzer.py`:

```python
import warnings

# At the top of perform_random_effects_meta_analysis
with warnings.catch_warnings():
    warnings.filterwarnings(
        'ignore',
        category=RuntimeWarning,
        message='invalid value encountered in sqrt',
        module='statsmodels.stats.meta_analysis'
    )
    result = meta.combine_effects(...)
```

This will suppress the noisy warnings while keeping other important warnings visible.

## References

- **DerSimonian-Laird Estimator:** Can produce negative tau² when heterogeneity is low
- **Statsmodels Documentation:** [meta_analysis module](https://www.statsmodels.org/stable/generated/statsmodels.stats.meta_analysis.combine_effects.html)
- **Meta-Analysis Best Practices:** Negative tau² is typically set to 0 (no between-study variance)
