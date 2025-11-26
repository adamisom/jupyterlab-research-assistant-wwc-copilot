# User Guide

Welcome to the JupyterLab Research Assistant & WWC Co-Pilot! This guide will help you get started with discovering, managing, and analyzing academic research papers directly within JupyterLab.

## Getting Started

### Installation

If you haven't already installed the extension:

```bash
pip install jupyterlab-research-assistant-wwc-copilot
```

Then restart JupyterLab:

```bash
jupyter lab
```

### Opening the Extension

The extension adds a **Research Library** panel to the left sidebar of JupyterLab. To open it:

1. **Look for the Research Library icon** in the left sidebar (it appears alongside File Browser, Running, etc.)
2. **Click the icon** to open the Research Library panel
3. **Or use the Command Palette**: Press `Cmd+Shift+C` (Mac) or `Ctrl+Shift+C` (Windows/Linux), then type "Research Library" and select "Open Research Library"

The Research Library panel has two main tabs:

- **Discovery**: Search and import papers from Semantic Scholar and OpenAlex
- **Library**: Browse and manage your imported papers

---

## Feature 1: Research Library & Discovery Engine

### Discovering Papers

#### Using the Discovery Tab

1. **Open the Research Library panel** (see above)
2. **Click the "Discovery" tab** at the top of the panel
3. **Enter a search query** in the search box (e.g., "spaced repetition learning", "peer tutoring mathematics")
4. **Click "Search"** or press Enter

The extension searches **Semantic Scholar** first, and automatically falls back to **OpenAlex** if Semantic Scholar is unavailable or rate-limited. No API keys required!

#### Search Results

Each result shows:

- **Title** and **authors**
- **Publication year**
- **Abstract** (if available)
- **Citation count**
- **DOI** (if available)

#### Importing Papers

To add a paper to your library:

1. **Click "Import"** on any search result
2. The paper is added to your local library
3. You'll see a success notification

**Note**: Papers imported from search results are "metadata-only" (title, authors, abstract, etc.). To use them for meta-analysis or WWC assessment, you'll need to upload the PDF and extract effect size data (see below).

### Managing Your Library

#### Using the Library Tab

1. **Click the "Library" tab** in the Research Library panel
2. Browse all your imported papers
3. **Search your library** using the search bar at the top
4. **Click any paper card** to view detailed information

#### Paper Cards

Each paper card displays:

- **Title** (clickable to open detail view)
- **Authors** (formatted as names)
- **Year** and **citation count**
- **WWC rating badge** (if assessment has been completed)
- **Hover effects** for better interactivity

#### Paper Detail View

Click any paper card to see:

- Complete metadata (title, authors, year, DOI, abstract)
- **Study metadata** (if available): methodology, sample sizes, effect sizes
- **Learning science metadata** (if available): domain, intervention type, age group
- **Actions**:
  - **"Open PDF"** button (if PDF is available)
  - **"Synthesize"** button (appears when 2+ papers are selected)
  - **"WWC Co-Pilot"** button to assess study quality

### Importing PDFs

You can import PDF files in two ways:

#### Method 1: File Picker

1. **Use the Command Palette**: `Cmd+Shift+C` → "Import PDF"
2. **Or use the Discovery tab**: Click "Import PDF" button
3. **Select a PDF file** from your computer
4. The extension will:
   - Extract text from the PDF
   - Optionally extract metadata using AI (if configured)
   - Save the PDF to your library

#### Method 2: File Browser Context Menu

1. **Right-click a PDF file** in JupyterLab's file browser
2. **Select "Import to Research Library"**
3. The PDF is imported automatically

#### AI Metadata Extraction (Optional)

If you've configured AI extraction (Claude, OpenAI, or Ollama), the extension can automatically extract:

- **Effect sizes** (Cohen's d, standard errors) by outcome
- **Sample sizes** (baseline and endline)
- **Methodology** (RCT, Quasi-experimental, etc.)
- **Learning science metadata** (domain, intervention type, age group)

**To configure AI extraction**: See the extension settings in JupyterLab (Settings → Advanced Settings → Research Assistant).

### Exporting Your Library

Export your library in multiple formats:

1. **Use the Command Palette**: `Cmd+Shift+C` → "Export Library"
2. **Or use the Library tab**: Click the export button
3. **Choose format**:
   - **CSV**: For spreadsheet analysis
   - **JSON**: For programmatic access
   - **BibTeX**: For LaTeX/Bibliography management

---

## Feature 2: Synthesis Engine

The Synthesis Engine provides powerful tools for analyzing and synthesizing findings across multiple studies. All synthesis features work with 2 or more papers selected from your library.

### Meta-Analysis

Perform statistical meta-analysis across multiple studies to synthesize effect sizes.

#### Running Meta-Analysis

1. **Select 2 or more papers** from your library (use checkboxes)
2. **Click "Synthesize Studies"** button
3. The **Synthesis Workbench** opens in the main area
4. **Click the "Meta-Analysis" tab**
5. **Click "Run Meta-Analysis"**

**Requirements**: Papers must have effect size data (`study_metadata.effect_sizes`). Papers imported from search results won't have this until you upload PDFs and extract metadata.

#### Meta-Analysis Results

The results display:

**Summary Statistics**:

- **Pooled effect size** (Cohen's d) with 95% confidence interval
- **P-value** for the overall effect
- **Heterogeneity statistics**:
  - **I²**: Percentage of variance due to heterogeneity
  - **tau²**: Between-study variance
  - **Q statistic**: Test of heterogeneity

**Visualization**:

- **Forest plot**: Shows individual study effect sizes with confidence intervals and the pooled estimate

**Individual Studies Table**:

- Effect size for each study
- Confidence intervals
- Study weights in the meta-analysis

**Export**: Click "Export as CSV" to download the results for further analysis.

### Subgroup Analysis

Explore how effect sizes vary across different subgroups.

#### Running Subgroup Analysis

1. **Open Synthesis Workbench** with 2+ papers
2. **Click "Subgroup Analysis" tab**
3. **Select a subgroup variable**:
   - Age group (e.g., elementary, middle school, high school)
   - Intervention type (e.g., tutoring, technology, curriculum)
   - Learning domain (e.g., cognitive, affective)
4. **Click "Run Analysis"**

**Requirements**: Papers must have subgroup metadata in `learning_science_metadata`.

#### Subgroup Results

- **Separate meta-analyses** for each subgroup
- **Comparison statistics** showing differences between subgroups
- **Forest plots** for each subgroup

### Publication Bias Assessment

Detect potential publication bias using statistical tests and visualizations.

#### Running Bias Assessment

1. **Open Synthesis Workbench** with 3+ papers
2. **Click "Bias Assessment" tab**
3. **Click "Run Assessment"**

#### Bias Results

**Egger's Test**:

- P-value indicating presence of publication bias
- Interpretation guidance

**Funnel Plot**:

- Visual representation of effect sizes vs. standard errors
- Asymmetry suggests potential publication bias
- Studies with larger standard errors (less precise) should show more scatter

### Sensitivity Analysis

Identify influential studies that might be driving your meta-analysis results.

#### Running Sensitivity Analysis

1. **Open Synthesis Workbench** with 2+ papers
2. **Click "Sensitivity Analysis" tab**
3. **Click "Run Analysis"**

#### Sensitivity Results

**Leave-One-Out Analysis**:

- Shows how the pooled effect size changes when each study is removed
- Helps identify influential studies
- Displays:
  - Pooled effect with each study removed
  - Confidence intervals
  - Difference from the full analysis

Use this to:

- Check robustness of your findings
- Identify studies that might be outliers
- Understand the contribution of each study

### Conflict Detection

Automatically detect contradictions between study findings using AI.

#### Running Conflict Detection

1. **Open Synthesis Workbench** with 2+ papers
2. **Click "Conflict Detection" tab**
3. **Click "Detect Conflicts"**

#### How It Works

1. **Finding Extraction**: The system extracts key findings from each paper's abstract or full text
2. **AI Comparison**: Uses Natural Language Inference (NLI) models to compare findings
3. **Contradiction Detection**: Flags pairs of findings that contradict each other

#### Conflict Results

Each detected contradiction shows:

- **Paper 1** and **Paper 2** titles
- **Finding 1** and **Finding 2** (the contradictory statements)
- **Confidence score** (how confident the model is about the contradiction)

**Note**: The system filters out comparisons between findings about different topics/interventions to reduce false positives.

**Requirements**: Conflict detection requires the optional `transformers` and `torch` libraries. Install with:

```bash
pip install "jupyterlab-research-assistant-wwc-copilot[conflict-detection]"
```

The first run will download the NLI model (~500MB-1GB), so it may be slower.

### Exporting Synthesis Reports

Generate comprehensive synthesis reports:

1. **In Synthesis Workbench**, click **"Export Synthesis Report"**
2. **Choose format**: Markdown (recommended) or other formats
3. The report includes:
   - Meta-analysis results
   - Subgroup analyses (if run)
   - Publication bias assessment (if run)
   - Sensitivity analysis (if run)
   - Detected conflicts (if run)
   - Complete references for all papers

---

## Feature 3: WWC Co-Pilot

The WWC Co-Pilot helps you assess individual study quality using **What Works Clearinghouse (WWC) Standards Handbook v5.0**.

### WWC Quality Assessment

#### Opening WWC Co-Pilot

1. **Select a paper** from your library (click the paper card)
2. **Click "WWC Co-Pilot"** in the detail view
3. The WWC assessment wizard opens in the main area

#### The Assessment Process

The WWC Co-Pilot guides you through a **5-step process**:

**Step 1: Randomization**

- Indicate whether randomization was documented
- Review extracted randomization information (if available)

**Step 2: Attrition**

- Review calculated attrition rates (overall and differential)
- Choose attrition boundary: **Cautious** or **Optimistic**
  - **Cautious**: Use when intervention could affect retention (e.g., dropout prevention programs)
  - **Optimistic**: Use when intervention is unlikely to affect retention (e.g., supplemental curriculum)
- See real-time calculation of whether attrition meets WWC standards

**Step 3: Baseline Equivalence**

- Review baseline differences between treatment and control groups
- See calculated effect size (Cohen's d) for baseline differences
- Color-coded indicators show whether equivalence is satisfied

**Step 4: Statistical Adjustment**

- Indicate if valid statistical adjustments were used (if required)
- Review adjustment methods reported in the study

**Step 5: Review & Finalize**

- See the **final WWC rating**:
  - 🟢 **Meets WWC Standards Without Reservations**
  - 🟡 **Meets WWC Standards With Reservations**
  - 🔴 **Does Not Meet WWC Standards**
- Review the **justification** for the rating
- Save the assessment (automatically stored in your library)

**Progress Tracking**: The wizard shows your progress and saves your work as you go (using localStorage).

---

## Workflow Examples

### Example 1: Quick Literature Review

1. **Search for papers**: Discovery tab → Search "peer tutoring reading"
2. **Import relevant papers**: Click "Import" on 5-10 papers
3. **Browse your library**: Library tab → Review imported papers
4. **Export bibliography**: Export as BibTeX for your paper

### Example 2: Systematic Review with Quality Assessment

1. **Import papers**: Use Discovery tab or upload PDFs
2. **Assess each study**: Open each paper → Click "WWC Co-Pilot" → Complete assessment
3. **Filter by quality**: In Library tab, filter to show only "Meets WWC Standards" papers
4. **Run meta-analysis**: Select 2+ high-quality papers → Synthesize → Meta-Analysis tab
5. **Assess bias**: Bias Assessment tab → Check for publication bias
6. **Export report**: Export synthesis report for your review

### Example 3: Exploring Intervention Effectiveness

1. **Import papers** on a specific intervention (e.g., "spaced repetition")
2. **Run meta-analysis**: Synthesize → Meta-Analysis → See overall effect
3. **Subgroup analysis**: Subgroup Analysis tab → Compare by age group
4. **Sensitivity analysis**: Identify which studies are most influential
5. **Check conflicts**: See if any studies contradict each other

---

## Tips & Best Practices

### For Synthesis Features

- **Effect sizes are required**: Papers need `study_metadata.effect_sizes` data for meta-analysis
- **Upload PDFs**: Papers from search results are metadata-only. Upload PDFs and use AI extraction to get effect sizes
- **Minimum 2 studies**: Meta-analysis requires at least 2 papers with effect sizes
- **More is better**: 3+ studies recommended for reliable results
- **Subgroup metadata**: Papers need `learning_science_metadata` for subgroup analysis

### For WWC Assessment

- **Sample sizes matter**: WWC assessment needs baseline and endline sample sizes
- **Attrition data**: Treatment and control group attrition rates are required
- **Choose boundary carefully**: The cautious/optimistic boundary choice affects the rating
- **Review extracted data**: Always verify that AI-extracted data is accurate

### For Conflict Detection

- **First run is slow**: The NLI model downloads on first use (~500MB-1GB)
- **Review findings**: Check the extracted findings to ensure they're accurate
- **False positives**: The system filters different topics, but review all conflicts manually
- **GPU support**: For faster processing, configure GPU support (see README)

### General Tips

- **Use search effectively**: Try different search terms, use year filters
- **Organize your library**: Use the search function to find papers quickly
- **Save your work**: WWC assessments and synthesis results are saved automatically
- **Export regularly**: Export your library periodically as a backup

---

## Troubleshooting

### Extension Not Appearing

1. **Check installation**: `jupyter labextension list` should show the extension
2. **Check server extension**: `jupyter server extension list` should show it enabled
3. **Restart JupyterLab**: Full restart (Ctrl+C, then `jupyter lab`) is required after installation

### Papers Not Showing Effect Sizes

- Papers imported from search are metadata-only
- Upload the PDF and use AI extraction to get effect sizes
- Or manually add effect size data (for developers)

### Meta-Analysis Fails

- Ensure you have 2+ papers with effect size data
- Check that papers have `study_metadata.effect_sizes` in the database
- Verify effect sizes are in correct format: `{"d": <cohen's_d>, "se": <standard_error>}`

### Conflict Detection Not Working

- Install optional dependencies: `pip install "jupyterlab-research-assistant-wwc-copilot[conflict-detection]"`
- First run downloads the model (be patient)
- Check browser console for errors

### Need More Help?

- Check the [Developer Guide](./docs/developer-guide.md) for technical details
- Open an issue on [GitHub](https://github.com/adamisom/jupyterlab-research-assistant-wwc-copilot/issues)
- Reach out to the author directly on [Twitter](https://x.com/adam__isom)

---

## Keyboard Shortcuts

- **Command Palette**: `Cmd+Shift+C` (Mac) or `Ctrl+Shift+C` (Windows/Linux)
- **Open Research Library**: Command Palette → "Open Research Library"
- **Import PDF**: Command Palette → "Import PDF"
- **Export Library**: Command Palette → "Export Library"

---

## What's Next?

Now that you're familiar with the extension, try:

1. **Import a set of papers** on a topic you're researching
2. **Run WWC assessments** on a few studies
3. **Perform a meta-analysis** with papers that have effect sizes
4. **Explore subgroup differences** in your research area
5. **Generate a synthesis report** for your review

Happy researching! 📚🔬
