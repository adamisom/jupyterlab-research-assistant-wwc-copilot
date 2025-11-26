# Developer Guide

This guide provides information for developers working on the JupyterLab Research Assistant & WWC Co-Pilot extension.

## Testing

### Adding Test Papers with Effect Sizes

To test meta-analysis features (meta-analysis, bias assessment, sensitivity analysis, subgroup analysis) and WWC assessment, you need papers with effect size data and sample sizes.

Use the test script to add sample papers:

```bash
python scripts/test_add_papers_with_effect_sizes.py
```

This script adds 5 test papers with:
- **Effect sizes** for meta-analysis features
- **Sample sizes** (baseline and endline) for attrition calculations
- **Attrition rates** (treatment and control) for WWC assessment
- **Subgroup metadata** (age_group, intervention_type, learning_domain) for subgroup analysis
- **Baseline equivalence data** (for one paper) for testing baseline equivalence checks

After running the script, you can test:
- **Meta-analysis** (requires 2+ papers with effect sizes)
- **Bias assessment** (requires 3+ papers with effect sizes)
- **Sensitivity analysis** (requires 3+ papers with effect sizes)
- **Subgroup analysis** (requires 2+ papers with effect sizes and subgroup metadata)
- **WWC Assessment** (requires sample sizes and attrition data)

**Note for WWC Assessment**: For a study to pass WWC standards, you need to:
1. Set "Randomization Documented" = `true` in the assessment
2. Choose an attrition boundary (cautious or optimistic)
3. The test papers have low attrition rates that should pass with the "optimistic" boundary

