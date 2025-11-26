# Developer Guide

This guide provides information for developers working on the JupyterLab Research Assistant & WWC Co-Pilot extension.

## Meta-Analysis Data Flow

### How Meta-Analysis Works

Meta-analysis uses **structured study metadata** stored in the database, not the full PDF text. Specifically, it reads from `study_metadata.effect_sizes` which contains structured effect size data (Cohen's d and standard errors).

**Data Source:**
- Meta-analysis reads from `paper.study_metadata.effect_sizes` (database field)
- Each effect size entry has: `{"d": <cohen's_d>, "se": <standard_error>}`
- The analysis can target a specific outcome name or use the first available outcome

**Why this matters:**
- Papers imported from discovery sources (Semantic Scholar, OpenAlex) are "metadata-only" and don't have `study_metadata.effect_sizes`
- These papers cannot be used for meta-analysis until effect sizes are added
- The UI prevents synthesis with metadata-only papers for this reason

### How PDF Upload Populates Study Metadata

When a PDF is uploaded, the system can extract structured metadata using AI:

1. **PDF Text Extraction**: The `PDFParser` extracts `full_text` from the PDF file
2. **AI Extraction (Optional)**: If AI extraction is enabled (`ai_config.enabled = true`), the `AIExtractor` processes the full text using the `LEARNING_SCIENCE_EXTRACTION_SCHEMA`
3. **Metadata Population**: The AI extracts structured data including:
   - `study_metadata.effect_sizes` - Effect sizes by outcome name
   - `study_metadata.methodology` - Research methodology (RCT, Quasi-experimental, etc.)
   - `study_metadata.sample_size_baseline/endline` - Sample sizes
   - `learning_science_metadata` - Domain, intervention type, age group, etc.
4. **Database Storage**: The extracted metadata is saved to the `study_metadata` and `learning_science_metadata` tables

**Important Notes:**
- AI extraction is **optional** - PDFs can be uploaded without it
- If AI extraction fails or is disabled, the PDF is still saved but `effect_sizes` may be empty
- Papers without `effect_sizes` cannot be used for meta-analysis
- The test script (`scripts/test_add_papers_with_effect_sizes.py`) bypasses this workflow and directly adds papers with effect sizes to the database

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

