# Code Analysis Report

A high-level overview of the JupyterLab Research Assistant & WWC
Co-Pilot extension codebase, covering all major components and their
relationships.

## Project Overview

This is a **JupyterLab extension** (frontend + server extension) that
provides two main features:

1. **Research Library & Discovery Engine** (Stage 1): Discover, import,
   and manage academic papers with Semantic Scholar integration, PDF
   parsing, and AI-powered metadata extraction
2. **WWC Co-Pilot & Synthesis Engine** (Stage 2): Perform WWC quality
   assessments, meta-analysis, conflict detection, subgroup analysis,
   publication bias assessment, and sensitivity analysis

**Architecture**: Frontend (TypeScript/React) communicates with backend
(Python) via REST API endpoints. Data is stored in SQLite database.

---

## Entry Points

### Backend Entry Point

- **`jupyterlab_research_assistant_wwc_copilot/__init__.py`**
  - Defines `_load_jupyter_server_extension()` which calls
    `setup_route_handlers()` from `routes.py`
  - Registers the server extension with JupyterLab
  - Entry point for all backend functionality

### Frontend Entry Point

- **`src/index.tsx`**
  - Main plugin definition (`JupyterFrontEndPlugin`)
  - Registers commands, creates widgets, sets up event listeners
  - Integrates with JupyterLab's command palette, file browser, and layout restorer
  - Creates and tracks `ResearchLibraryPanel` and `SynthesisWorkbench` widgets

---

## Backend Architecture (Python)

### Core Structure

```text
jupyterlab_research_assistant_wwc_copilot/
├── __init__.py              # Server extension entry point
├── routes.py                 # All API route handlers (single file)
├── database/
│   └── models.py             # SQLAlchemy ORM models (Paper, StudyMetadata, LearningScienceMetadata)
└── services/                 # Business logic modules
    ├── semantic_scholar.py   # Semantic Scholar API client
    ├── openalex.py            # OpenAlex API client (fallback for discovery)
    ├── pdf_parser.py         # PDF text extraction (PyMuPDF)
    ├── ai_extractor.py       # AI metadata extraction (Claude/GPT/Ollama)
    ├── extraction_schema.py # JSON schemas for AI extraction
    ├── db_manager.py         # Database session management
    ├── import_service.py     # PDF import orchestration
    ├── export_formatter.py   # Export to JSON/CSV/BibTeX/Markdown
    ├── wwc_assessor.py       # WWC quality assessment engine
    ├── meta_analyzer.py     # Meta-analysis (statsmodels)
    ├── visualizer.py         # Forest plots, funnel plots (matplotlib)
    └── conflict_detector.py  # Conflict detection (NLI models)
```

### API Routes (`routes.py`)

All routes extend `BaseAPIHandler` and are registered in
`setup_route_handlers()`. Routes are prefixed with
`/jupyterlab-research-assistant-wwc-copilot/`:

**Stage 1 Routes:**

- `GET /hello` - Health check
- `GET /library` - Get all papers
- `POST /library` - Add paper
- `GET /search?q=...` - Search library
- `GET /discovery?q=...` - Search Semantic Scholar (with OpenAlex fallback)
- `POST /import` - Import PDF file
- `GET /export?format=...` - Export library (JSON/CSV/BibTeX)
- `GET /pdf?paper_id=...` - Serve PDF file for viewing

**Stage 2 Routes:**

- `POST /wwc-assessment` - Run WWC quality assessment
- `POST /meta-analysis` - Perform meta-analysis
- `POST /conflict-detection` - Detect conflicts between papers
- `POST /subgroup-analysis` - Subgroup meta-analysis
- `POST /bias-assessment` - Publication bias (Egger's test, funnel plot)
- `POST /sensitivity-analysis` - Leave-one-out sensitivity analysis
- `POST /meta-analysis/export` - Export meta-analysis as CSV
- `POST /synthesis/export` - Export synthesis report as Markdown

### Database Models (`database/models.py`)

**Paper** (main table):

- Core fields: `id`, `title`, `authors` (JSON), `year`, `doi`, `s2_id`,
  `citation_count`, `pdf_path`, `abstract`, `full_text`
- Relationships: `study_metadata`, `learning_science_metadata`

**StudyMetadata**:

- `paper_id` (FK), `methodology`, `sample_size_baseline`,
  `sample_size_endline`, `effect_sizes` (JSON)

**LearningScienceMetadata**:

- `paper_id` (FK), `learning_domain`, `intervention_type`, `age_group`

Database file: `~/.jupyter/research_assistant/research_library.db` (SQLite)

### Key Services

**`wwc_assessor.py`** - WWC Quality Assessment Engine:

- Implements WWC Handbook v5.0 decision rules
- `WWCQualityAssessor.assess()` - Main assessment method
- Calculates attrition thresholds (cautious/optimistic boundaries)
- Checks baseline equivalence (Cohen's d thresholds)
- Returns `WWCAssessment` dataclass with final rating

**`meta_analyzer.py`** - Meta-Analysis Engine:

- `perform_random_effects_meta_analysis()` - Random-effects meta-analysis
  using statsmodels
- `perform_subgroup_meta_analysis()` - Subgroup comparisons
- `perform_eggers_test()` - Publication bias test
- `perform_sensitivity_analysis()` - Leave-one-out analysis
- Returns pooled effect, confidence intervals, heterogeneity statistics
  (I², Q)

**`visualizer.py`** - Plot Generation:

- `create_forest_plot()` - Forest plot (base64 PNG)
- `create_funnel_plot()` - Funnel plot for bias assessment

**`conflict_detector.py`** - Conflict Detection:

- `extract_key_findings()` - Extract findings from paper text
- `find_contradictions()` - Use NLI model to detect contradictions

**`import_service.py`** - PDF Import Orchestration:

- Coordinates PDF parsing, AI extraction, and database storage
- `import_pdf()` - Main import method

---

## Frontend Architecture (TypeScript/React)

### Frontend Structure

```text
src/
├── index.tsx                 # Plugin entry point, command registration
├── request.ts                # Low-level API request helper (uses ServerConnection)
├── api.ts                    # Typed API client functions (all backend calls)
├── widgets/                  # React components
│   ├── ResearchLibraryPanel.tsx    # Main sidebar panel (Discovery + Library tabs)
│   ├── DiscoveryTab.tsx           # Semantic Scholar/OpenAlex search UI
│   ├── LibraryTab.tsx              # Local library view with search/filter
│   ├── SearchBar.tsx               # Reusable search input component
│   ├── Tabs.tsx                     # Reusable tab navigation component
│   ├── PaperCard.tsx               # Paper card component
│   ├── DetailView.tsx              # Paper detail view
│   ├── WWCCoPilot.tsx              # WWC assessment wizard (main area widget)
│   ├── SynthesisWorkbench.tsx     # Synthesis dashboard (main area widget)
│   ├── MetaAnalysisView.tsx        # Meta-analysis results display
│   ├── ConflictView.tsx            # Conflict detection results
│   ├── SubgroupAnalysisView.tsx    # Subgroup analysis results
│   ├── BiasAssessmentView.tsx      # Publication bias results
│   ├── SensitivityAnalysisView.tsx # Sensitivity analysis results
│   ├── LoadingState.tsx            # Loading indicator component
│   ├── ErrorDisplay.tsx            # Error message display component
│   └── SkeletonLoader.tsx          # Skeleton loading placeholder
└── utils/                    # Utility modules
    ├── api-response.ts       # Response handling/validation
    ├── download.ts           # File download helpers
    ├── events.ts             # Custom event system (AppEvents)
    ├── format.ts             # Number/date formatting
    ├── hooks.ts              # React hooks (useAsyncOperation)
    ├── notifications.ts      # Error/success notifications
    ├── paper.ts              # Paper data utilities
    └── retry.ts              # Retry logic with backoff
```

### Widget Hierarchy

**Sidebar Widgets:**

- `ResearchLibraryPanel` - Main panel with tabs
  - `DiscoveryTab` - Search Semantic Scholar, import papers
  - `LibraryTab` - Browse/search local library, open detail view, launch
    synthesis

**Main Area Widgets:**

- `WWCCoPilot` - WWC assessment wizard (5-step process)
- `SynthesisWorkbench` - Synthesis dashboard with tabs for meta-analysis,
  conflicts, subgroups, bias, sensitivity

### API Client (`api.ts`)

All backend communication goes through typed functions in `api.ts`:

- `getLibrary()`, `searchLibrary()`, `searchSemanticScholar()`,
  `importPaper()`, `importPDF()`, `exportLibrary()`
- `runWWCAssessment()`, `performMetaAnalysis()`, `detectConflicts()`,
  `performSubgroupAnalysis()`, `assessPublicationBias()`,
  `performSensitivityAnalysis()`

All functions use `requestAPI()` from `request.ts` which handles
authentication and base URL construction.

### Command System (`index.tsx`)

Commands registered with JupyterLab:

- `jupyterlab-research-assistant-wwc-copilot:open-library` - Open research
  library panel
- `jupyterlab-research-assistant-wwc-copilot:import-pdf` - Import PDF
  dialog
- `jupyterlab-research-assistant-wwc-copilot:export-library` - Export
  library dialog
- `jupyterlab-research-assistant-wwc-copilot:open-synthesis` - Open
  synthesis workbench (requires paperIds)
- `jupyterlab-research-assistant-wwc-copilot:open-wwc` - Open WWC Co-Pilot
  (requires paperId)

Commands are added to command palette and can be triggered programmatically via `app.commands.execute()`.

### Event System (`utils/events.ts`)

Custom events for cross-component communication:

- `AppEvents.onOpenSynthesisWorkbench()` - LibraryTab → SynthesisWorkbench
- `AppEvents.onOpenWWCCopilot()` - DetailView → WWCCoPilot

---

## Data Flow

### Paper Import Flow

1. **User uploads PDF** → `index.tsx` command handler
2. **Frontend** → `api.ts:importPDF()` → `POST /import`
3. **Backend** → `ImportHandler.post()` → `ImportService.import_pdf()`
4. **ImportService** orchestrates:
   - `PDFParser.extract_text_and_metadata()` - Extract text
   - `AIExtractor.extract_metadata()` (optional) - AI extraction
   - `DatabaseManager.add_paper()` - Store in database
5. **Response** → Frontend updates library view

### Paper Discovery Flow

1. **User searches** → `DiscoveryTab` component
2. **Frontend** → `api.ts:searchSemanticScholar()` →
   `GET /discovery?q=...`
3. **Backend** → `DiscoveryHandler.get()`:
   - Attempts `SemanticScholarAPI.search_papers()`
   - If Semantic Scholar fails or is rate-limited, automatically falls back to `OpenAlexAPI.search_papers()`
4. **Response** → Display results, user can import

### WWC Assessment Flow

1. **User opens WWC Co-Pilot** → `DetailView` triggers event →
   `index.tsx` creates `WWCCoPilot` widget
2. **User makes judgments** → `WWCCoPilot` component state
3. **Frontend** → `api.ts:runWWCAssessment()` → `POST /wwc-assessment`
4. **Backend** → `WWCAssessmentHandler.post()` → `WWCQualityAssessor.assess()`
5. **WWCQualityAssessor**:
   - Fetches paper from database
   - Calculates attrition (overall, differential)
   - Checks baseline equivalence
   - Applies WWC decision rules
   - Returns `WWCAssessment` with final rating
6. **Response** → `WWCCoPilot` displays results

### Meta-Analysis Flow

1. **User selects papers** → `LibraryTab` → Opens `SynthesisWorkbench`
2. **User runs meta-analysis** → `SynthesisWorkbench` → `api.ts:performMetaAnalysis()`
3. **Backend** → `MetaAnalysisHandler.post()`:
   - Fetches papers from database
   - Extracts effect sizes from `study_metadata.effect_sizes`
   - Calls `MetaAnalyzer.perform_random_effects_meta_analysis()`
   - Generates forest plot via `Visualizer.create_forest_plot()`
4. **Response** → `MetaAnalysisView` displays results and forest plot

### Conflict Detection Flow

1. **User runs conflict detection** → `SynthesisWorkbench` → `api.ts:detectConflicts()`
2. **Backend** → `ConflictDetectionHandler.post()`:
   - Fetches papers from database
   - `ConflictDetector.extract_key_findings()` - Extract findings from text
   - `ConflictDetector.find_contradictions()` - Compare findings with NLI model
3. **Response** → `ConflictView` displays contradictions

---

## Key Relationships

### Backend → Frontend Communication

- **Routes** (`routes.py`) define API endpoints
- **API Client** (`api.ts`) provides typed functions that call these endpoints
- **Widgets** call API functions, handle responses, update UI

### Database → Services → Routes

- **Models** (`models.py`) define schema
- **DatabaseManager** (`db_manager.py`) provides session management and CRUD operations
- **Services** use `DatabaseManager` to query/insert data
- **Route handlers** use services and `DatabaseManager` to process requests

### Widget Communication

- **Commands** (`index.tsx`) - Global commands accessible via palette
- **Events** (`utils/events.ts`) - Custom events for cross-component communication
- **Props** - Direct parent-child communication

### External Dependencies

**Backend:**

- `sqlalchemy` - ORM and database
- `statsmodels` - Meta-analysis
- `matplotlib` - Plot generation
- `transformers` (optional) - NLI models for conflict detection
- `requests` - HTTP client for Semantic Scholar and OpenAlex APIs
- `PyMuPDF` (fitz) - PDF parsing
- `openai` / `anthropic` - AI extraction (optional)

**Frontend:**

- `@jupyterlab/application` - JupyterLab core
- `@jupyterlab/apputils` - Widgets, dialogs, notifications
- `@jupyterlab/services` - ServerConnection for API calls
- `react` - UI framework

---

## Component Responsibilities

### Backend Services

- **`semantic_scholar.py`**: Semantic Scholar API client, rate limiting
- **`openalex.py`**: OpenAlex API client (fallback for discovery), rate limiting
- **`pdf_parser.py`**: PDF text extraction using PyMuPDF
- **`ai_extractor.py`**: AI metadata extraction (configurable provider: Claude, OpenAI, Ollama)
- **`extraction_schema.py`**: JSON schemas defining metadata extraction structure (learning science schema)
- **`db_manager.py`**: Database session context manager, CRUD operations
- **`import_service.py`**: Orchestrates PDF import workflow (parsing → AI extraction → storage)
- **`export_formatter.py`**: Formats data for export (JSON/CSV/BibTeX/Markdown)
- **`wwc_assessor.py`**: WWC quality assessment logic (implements WWC Handbook v5.0)
- **`meta_analyzer.py`**: Statistical meta-analysis (random-effects, subgroup, sensitivity)
- **`visualizer.py`**: Plot generation (forest plots, funnel plots) using matplotlib
- **`conflict_detector.py`**: Natural language inference for conflict detection (NLI models)

### Frontend Widgets

- **`ResearchLibraryPanel`**: Main sidebar container with tab navigation
- **`DiscoveryTab`**: Search and import from Semantic Scholar/OpenAlex
- **`LibraryTab`**: Browse local library, search, filter, select papers
- **`SearchBar`**: Reusable search input component with debouncing
- **`Tabs`**: Reusable tab navigation component
- **`PaperCard`**: Individual paper card display with metadata preview
- **`DetailView`**: Display paper metadata, launch WWC assessment, view PDF
- **`WWCCoPilot`**: 5-step WWC assessment wizard with localStorage persistence
- **`SynthesisWorkbench`**: Tabbed interface for synthesis analyses
- **`MetaAnalysisView`**: Display meta-analysis results and forest plot
- **`ConflictView`**: Display detected contradictions with confidence scores
- **`SubgroupAnalysisView`**: Display subgroup analysis results with comparisons
- **`BiasAssessmentView`**: Display publication bias results (Egger's test) and funnel plot
- **`SensitivityAnalysisView`**: Display sensitivity analysis results (leave-one-out)
- **`LoadingState`**: Loading indicator for async operations
- **`ErrorDisplay`**: Error message display with retry options
- **`SkeletonLoader`**: Skeleton loading placeholder for better UX

### Utilities

- **`api-response.ts`**: Validates and extracts data from API responses
- **`retry.ts`**: Retry logic with exponential backoff
- **`download.ts`**: File download helpers
- **`format.ts`**: Number/date formatting utilities
- **`hooks.ts`**: React hooks for async operations
- **`notifications.ts`**: User-facing error/success messages
- **`events.ts`**: Custom event system for cross-component communication

---

## Configuration

### Settings Schema (`schema/plugin.json`)

Defines JupyterLab settings for:

- AI extraction configuration (provider, API key, model, etc.)

### Server Extension Config (`jupyter-config/server-config/...`)

Enables the server extension in JupyterLab.

---

## Testing

### Backend Tests (`jupyterlab_research_assistant_wwc_copilot/tests/`)

- Unit tests for services
- Integration tests for routes
- Test fixtures for database

### Frontend Tests (`src/utils/__tests__/`)

- Unit tests for utility functions
- Component tests (Jest + React Testing Library)

### Integration Tests (`ui-tests/`)

- Playwright tests for end-to-end workflows

---

## Build & Development

### Build Process

1. **TypeScript compilation**: `jlpm build` → compiles `src/` → `lib/`
2. **Extension bundling**: Creates `labextension/` directory
3. **Python package**: `pip install -e .` installs both frontend and backend

### Development Workflow

- **Frontend changes**: `jlpm watch` (auto-rebuild) → refresh browser
- **Backend changes**: Restart JupyterLab server
- **Database**: SQLite file in `~/.jupyter/research_assistant/`

---

## Key Design Patterns

1. **Service Layer**: Business logic separated from route handlers
2. **Context Manager**: `DatabaseManager` uses context manager for session management
3. **Typed API**: Frontend API functions match backend response types
4. **Widget Tracking**: JupyterLab's `WidgetTracker` for panel restoration
5. **Command Pattern**: JupyterLab commands for global actions
6. **Event System**: Custom events for cross-component communication
7. **Error Handling**: Centralized error handling in `BaseAPIHandler` and `api-response.ts`

---

## Summary

This extension follows a **clear separation of concerns**:

- **Backend** handles data processing, external APIs, database, and
  statistical analysis
- **Frontend** handles UI, user interactions, and API communication
- **Database** stores papers and metadata
- **Services** encapsulate business logic
- **Routes** provide REST API interface
- **Widgets** provide user-facing components

The codebase is organized into logical modules with clear
responsibilities, making it maintainable and extensible.
