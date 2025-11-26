# Developer Guide

This guide provides information for developers working on the
JupyterLab Research Assistant & WWC Co-Pilot extension.

## Table of Contents

- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Meta-Analysis Data Flow](#meta-analysis-data-flow)
- [Common Development Tasks](#common-development-tasks)
- [Debugging](#debugging)
- [Architecture Reference](#architecture-reference)

## Development Setup

### Prerequisites

- Python >= 3.9
- Node.js (for building the extension)
- JupyterLab >= 4.0.0
- Git

### Initial Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/adamisom/jupyterlab-research-assistant-wwc-copilot.git
   cd jupyterlab-research-assistant-wwc-copilot
   ```

2. **Set up a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install the package in development mode:**
   ```bash
   pip install --editable ".[dev,test]"
   ```

4. **Link the extension with JupyterLab:**
   ```bash
   jupyter labextension develop . --overwrite
   jupyter server extension enable jupyterlab_research_assistant_wwc_copilot
   ```

5. **Build the extension:**
   ```bash
   jlpm build
   ```

6. **Start JupyterLab:**
   ```bash
   jupyter lab
   ```

### Development Uninstall

To remove the development installation:

```bash
# Disable server extension
jupyter server extension disable jupyterlab_research_assistant_wwc_copilot

# Uninstall Python package
pip uninstall jupyterlab_research_assistant_wwc_copilot

# Remove labextension symlink
# Find location: jupyter labextension list
# Then remove: rm <labextensions-path>/jupyterlab-research-assistant-wwc-copilot
```

## Project Structure

### Backend (Python)

```
jupyterlab_research_assistant_wwc_copilot/
├── __init__.py              # Server extension entry point
├── routes.py                 # All API route handlers
├── database/
│   └── models.py             # SQLAlchemy ORM models
└── services/                 # Business logic
    ├── semantic_scholar.py   # Semantic Scholar API client
    ├── openalex.py           # OpenAlex API client (fallback)
    ├── pdf_parser.py         # PDF text extraction
    ├── ai_extractor.py       # AI metadata extraction
    ├── extraction_schema.py  # JSON schemas for extraction
    ├── db_manager.py         # Database session management
    ├── import_service.py     # PDF import orchestration
    ├── export_formatter.py   # Export formatting
    ├── wwc_assessor.py       # WWC quality assessment
    ├── meta_analyzer.py      # Meta-analysis engine
    ├── visualizer.py         # Plot generation
    └── conflict_detector.py  # Conflict detection (NLI)
```

### Frontend (TypeScript/React)

```
src/
├── index.tsx                 # Plugin entry point
├── request.ts                # API request helper
├── api.ts                    # Typed API client functions
├── widgets/                  # React components
│   ├── ResearchLibraryPanel.tsx
│   ├── DiscoveryTab.tsx
│   ├── LibraryTab.tsx
│   ├── WWCCoPilot.tsx
│   ├── SynthesisWorkbench.tsx
│   └── [other components]
└── utils/                    # Utility modules
    ├── api-response.ts
    ├── events.ts
    ├── hooks.ts
    └── [other utilities]
```

## Development Workflow

### Watch Mode (Recommended)

For active development, use watch mode to automatically rebuild on changes:

```bash
# Terminal 1: Watch for changes
jlpm watch

# Terminal 2: Run JupyterLab
jupyter lab
```

With watch mode, changes to TypeScript files will automatically rebuild. Just refresh your browser to see changes.

### Manual Build

If not using watch mode:

```bash
# After making TypeScript changes
jlpm build

# Then refresh browser
```

### Backend Changes

For Python backend changes:

1. Make your changes to Python files
2. **Restart JupyterLab** (Ctrl+C, then `jupyter lab` again)
3. No rebuild needed for Python changes

**Memory aid**: "What did you change? Restart that!"
- Changed **TypeScript** → Build → Refresh browser
- Changed **Python** → Restart JupyterLab server

### Adding Dependencies

**Frontend dependencies:**
```bash
jlpm add <package-name>
jlpm build  # Rebuild after adding
```

**Backend dependencies:**
```bash
# Add to pyproject.toml under [project.dependencies] or [project.optional-dependencies]
pip install -e ".[dev,test]"  # Reinstall to pick up changes
```

## Testing

### Running Tests

**Backend tests (Pytest):**
```bash
pytest -vv -r ap --cov jupyterlab_research_assistant_wwc_copilot
```

**Frontend tests (Jest):**
```bash
jlpm test
```

**Integration tests (Playwright):**
```bash
cd ui-tests
jlpm install
jlpm playwright test
```

See [ui-tests/README.md](../ui-tests/README.md) for more integration test details.

### Adding Test Papers

To test meta-analysis and WWC features, you need papers with effect size data:

```bash
python scripts/test_add_papers_with_effect_sizes.py
```

This adds 5 test papers with:
- Effect sizes for meta-analysis
- Sample sizes for WWC assessment
- Subgroup metadata for subgroup analysis
- Baseline equivalence data

## Meta-Analysis Data Flow

### How Meta-Analysis Works

Meta-analysis uses **structured study metadata** stored in the database,
not the full PDF text. Specifically, it reads from
`study_metadata.effect_sizes` which contains structured effect size data
(Cohen's d and standard errors).

**Data Source:**

- Meta-analysis reads from `paper.study_metadata.effect_sizes`
  (database field)
- Each effect size entry has: `{"d": <cohen's_d>, "se": <standard_error>}`
- The analysis can target a specific outcome name or use the first
  available outcome

**Why this matters:**

- Papers imported from discovery sources (Semantic Scholar, OpenAlex) are
  "metadata-only" and don't have `study_metadata.effect_sizes`
- These papers cannot be used for meta-analysis until effect sizes are
  added
- The UI prevents synthesis with metadata-only papers for this reason

### How PDF Upload Populates Study Metadata

When a PDF is uploaded, the system can extract structured metadata using
AI:

1. **PDF Text Extraction**: The `PDFParser` extracts `full_text` from
   the PDF file
2. **AI Extraction (Optional)**: If AI extraction is enabled
   (`ai_config.enabled = true`), the `AIExtractor` processes the full
   text using the `LEARNING_SCIENCE_EXTRACTION_SCHEMA`
3. **Metadata Population**: The AI extracts structured data including:
   - `study_metadata.effect_sizes` - Effect sizes by outcome name
   - `study_metadata.methodology` - Research methodology (RCT,
     Quasi-experimental, etc.)
   - `study_metadata.sample_size_baseline/endline` - Sample sizes
   - `learning_science_metadata` - Domain, intervention type, age group,
     etc.
4. **Database Storage**: The extracted metadata is saved to the
   `study_metadata` and `learning_science_metadata` tables

**Important Notes:**

- AI extraction is **optional** - PDFs can be uploaded without it
- If AI extraction fails or is disabled, the PDF is still saved but
  `effect_sizes` may be empty
- Papers without `effect_sizes` cannot be used for meta-analysis
- The test script (`scripts/test_add_papers_with_effect_sizes.py`)
  bypasses this workflow and directly adds papers with effect sizes to
  the database

## Testing

### Adding Test Papers with Effect Sizes

To test meta-analysis features (meta-analysis, bias assessment,
sensitivity analysis, subgroup analysis) and WWC assessment, you need
papers with effect size data and sample sizes.

Use the test script to add sample papers:

```bash
python scripts/test_add_papers_with_effect_sizes.py
```

This script adds 5 test papers with:

- **Effect sizes** for meta-analysis features
- **Sample sizes** (baseline and endline) for attrition calculations
- **Attrition rates** (treatment and control) for WWC assessment
- **Subgroup metadata** (age_group, intervention_type, learning_domain)
  for subgroup analysis
- **Baseline equivalence data** (for one paper) for testing baseline
  equivalence checks

After running the script, you can test:

- **Meta-analysis** (requires 2+ papers with effect sizes)
- **Bias assessment** (requires 3+ papers with effect sizes)
- **Sensitivity analysis** (requires 3+ papers with effect sizes)
- **Subgroup analysis** (requires 2+ papers with effect sizes and
  subgroup metadata)
- **WWC Assessment** (requires sample sizes and attrition data)

**Note for WWC Assessment**: For a study to pass WWC standards, you need
to:

1. Set "Randomization Documented" = `true` in the assessment
2. Choose an attrition boundary (cautious or optimistic)
3. The test papers have low attrition rates that should pass with the
   "optimistic" boundary

## Common Development Tasks

### Adding a New API Endpoint

1. **Add route handler in `routes.py`:**
   ```python
   class MyNewHandler(BaseAPIHandler):
       @tornado.web.authenticated
       def post(self):
           data = self.get_json_body()
           # Process request
           result = {"status": "success", "data": ...}
           self.finish(result)
   ```

2. **Register in `setup_route_handlers()`:**
   ```python
   (url_path_join(base_url, route_prefix, "my-endpoint"), MyNewHandler),
   ```

3. **Add typed function in `src/api.ts`:**
   ```typescript
   export async function myNewFunction(params: MyParams): Promise<MyResponse> {
     return await requestAPI<MyResponse>('my-endpoint', {
       method: 'POST',
       body: JSON.stringify(params)
     });
   }
   ```

### Adding a New Widget Component

1. **Create component in `src/widgets/`:**
   ```typescript
   // MyNewWidget.tsx
   import React from 'react';
   
   export const MyNewWidget: React.FC<Props> = (props) => {
     // Component implementation
   };
   ```

2. **Import and use in parent component or `index.tsx`**

3. **Add styles in `style/index.css`** (use JupyterLab CSS variables)

### Modifying Database Schema

1. **Update models in `database/models.py`**
2. **Create migration** (if using Alembic in future)
3. **Update import/export services** if schema affects data flow
4. **Update frontend types** in `src/api.ts` if API responses change

### Debugging

**Frontend debugging:**
- Open browser DevTools (F12 or Cmd+Option+I)
- Check Console tab for JavaScript errors
- Check Network tab for failed API requests
- Use React DevTools extension for component inspection
- Source maps are enabled in dev mode for debugging

**Backend debugging:**
- Check JupyterLab server logs in terminal
- Add Python logging: `import logging; logger = logging.getLogger(__name__)`
- Use `print()` statements (they appear in server logs)
- Check database: SQLite file at `~/.jupyter/research_assistant/research_library.db`

**Common issues:**
- Extension not appearing: Check `jupyter labextension list` and `jupyter server extension list`
- API errors: Verify route is registered in `setup_route_handlers()`
- Type errors: Run `npx tsc --noEmit` to see all TypeScript errors
- Import errors: Check virtual environment is activated

## Architecture Reference

For detailed architecture information, see:
- **[Code Analysis Report](./code-analysis-report.md)**: Complete overview of all components
- **[JupyterLab Architecture](./jupyterlab-architecture.md)**: Deep dive into JupyterLab patterns
- **[Master Plan](./master-plan.md)**: High-level project architecture
- **[Getting Started](./getting-started.md)**: JupyterLab core development environment setup

## Additional Resources

- **[AGENTS.md](../AGENTS.md)**: Coding standards and best practices
- **[Styling Principles](./styling-principles.md)**: CSS and UI guidelines
