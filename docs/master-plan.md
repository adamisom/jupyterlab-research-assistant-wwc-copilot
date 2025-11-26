# JupyterLab WWC Co-Pilot: Master Implementation Plan (Extension Approach)

**Project Goal**: To develop a third-party JupyterLab extension with two substantial, end-to-end features that empower researchers to import, analyze, and synthesize academic literature, with a specialized focus on learning science research and What Works Clearinghouse (WWC) quality assessment.

**Guiding Principle**: The primary objective is to create a **"WWC Co-Pilot"**—a suite of tools that automates the tedious aspects of conducting rigorous literature reviews while scaffolding the critical human judgments required by WWC standards.

---

## Project Context: Why Build on JupyterLab?

JupyterLab is a web-based IDE for data science and scientific computing, used by millions of researchers. Building the WWC Co-Pilot as a JupyterLab extension is a strategic choice for several reasons:

### 1. Your Target Users Are Already There

Education researchers who do meta-analyses and systematic reviews are likely already using JupyterLab (or Jupyter Notebooks) for their statistical analysis. We are meeting them where they work.

### 2. Integrated Workflow

Instead of a fragmented workflow across multiple applications (Zotero, Excel, R, Word), researchers can do everything in one place: import PDFs in JupyterLab, extract metadata with our extension, run WWC quality assessment with our extension, run meta-analysis in a notebook cell, and generate reports in the same notebook.

### 3. Computational Context

Our features (PDF extraction, meta-analysis, forest plots) are computational tasks. JupyterLab is built for computational workflows. It makes sense to put research tools where the research computation happens.

### 4. Extensibility is the Core Philosophy

JupyterLab was designed from the ground up to be extended. Building a third-party extension is the intended way to add specialized functionality.

---

## Stage 0: Foundation & Extension Development Setup

**Objective**: Understand the JupyterLab ecosystem and set up a robust development environment for building a third-party extension.

### Phase 0.1: Architecture & Codebase Deep Dive

This phase focuses on understanding JupyterLab's core concepts and design patterns by studying both the documentation and existing third-party extensions.

**Key Activities**:

1. **Documentation Review**: Thoroughly read the official JupyterLab developer documentation, focusing on the extension development guides, architecture overviews, and the Lumino widget framework documentation [1].
2. **Study Existing Extensions**: Analyze the structure of 2-3 popular third-party extensions to understand real-world patterns:
    - **jupyterlab-git**: Demonstrates sidebar panels, server extensions, and complex state management.
    - **jupyterlab-lsp**: Shows how to integrate external services and provide real-time feedback.
    - **jupyterlab-drawio**: Illustrates custom document types and rendering.
3. **Pattern Identification**: Document key architectural patterns, including:
    - **Plugin System**: How plugins are defined, registered, and activated using tokens for dependency injection.
    - **Service & Token Model**: How different parts of the application provide and consume services.
    - **Lumino Widgets**: The lifecycle and structure of UI components, including panels, menus, and dialogs.
    - **Server Extensions**: The mechanism for adding backend functionality and creating REST APIs.

**Deliverable**: A personal architecture diagram illustrating how your extension will integrate with JupyterLab, showing the key extension points to be used and the anticipated data flow between the frontend and backend components.

### Phase 0.2: Development Environment & Build Process

This phase involves setting up a local development environment for extension development.

**Key Activities**:

1. **Environment Setup**: Install prerequisites (Git, Miniconda, Node.js LTS). Use `conda` to create an isolated environment for JupyterLab development [2].
2. **Install JupyterLab**: Install JupyterLab in your conda environment: `pip install jupyterlab`. This gives you a working JupyterLab instance to develop against.
3. **Verify Installation**: Launch JupyterLab (`jupyter lab`) to confirm it works correctly.

**Deliverable**: A fully functional local JupyterLab installation ready for extension development.

### Phase 0.3: Extension Scaffolding & Linking

This phase uses the official JupyterLab Extension Template to create your extension repository and link it to your local JupyterLab for rapid iteration.

**Key Activities**:

1. **Use the Extension Template**: Generate your extension using cookiecutter:

    ```bash
    pip install cookiecutter
    cookiecutter https://github.com/jupyterlab/extension-template
    ```

    Answer the prompts:
    - Extension name: `jupyterlab-research-assistant-wwc-copilot`
    - Has server extension: `Yes`
    - Has frontend extension: `Yes`

2. **Explore the Generated Structure**: Examine the scaffolded code to understand:
    - `src/`: Frontend TypeScript code
    - `jupyterlab_research_assistant/`: Backend Python code
    - `package.json`: Frontend dependencies and build scripts
    - `pyproject.toml`: Python package configuration

3. **Link for Development**: Install your extension in development mode:

    ```bash
    cd jupyterlab-research-assistant-wwc-copilot
    pip install -e .
    jupyter labextension develop . --overwrite
    jupyter server extension enable jupyterlab_research_assistant_wwc_copilot
    ```

4. **Test the Setup**: Run JupyterLab in development mode with auto-rebuild:

    ```bash
    jupyter lab --dev-mode --watch
    ```

    Verify that the template extension appears in JupyterLab (check the command palette or console for confirmation messages).

**Deliverable**: A working extension repository linked to your local JupyterLab, with live reloading enabled for rapid iteration.

### Phase 0.4: Community Integration

This phase focuses on engaging with the JupyterLab community to gather feedback, build relationships, and ensure your features align with community needs and standards.

**Key Activities**:

1. **Join Community Channels**: Join the JupyterLab community on [Discourse](https://discourse.jupyter.org/) or [Matrix/Element](https://matrix.to/#/#jupyterlab:matrix.org).
2. **Introduce Yourself**: Post a brief introduction explaining your background in learning science and your interest in building research tools for JupyterLab.
3. **Post an RFC (Request for Comments)**: Share your feature proposals with the community to gather early feedback. Use the template below:

**RFC Post Template**:

```markdown
Title: Proposal: WWC Co-Pilot & Research Assistant Extension for JupyterLab

Context: Researchers using JupyterLab for data analysis often work with academic papers but lack integrated tools for managing and synthesizing research literature, especially for conducting rigorous systematic reviews.

Proposed Features:

1. Research Library & Discovery Engine - Search Semantic Scholar, import PDFs, extract metadata, build searchable database
2. WWC Co-Pilot & Synthesis Engine - Assess study quality using WWC standards, perform meta-analysis, detect conflicts

Use Cases:

- Learning science researchers analyzing intervention studies
- Education researchers conducting What Works Clearinghouse reviews
- Meta-analysts comparing effect sizes across studies
- Systematic reviewers assessing research quality

Design Principles:

- Privacy-first (all processing local or user-controlled)
- Extensible (templates for different research domains)
- Follows JupyterLab patterns (Lumino widgets, command system)
- Human-in-the-loop for critical judgments

Questions for Community:

- Does this fit JupyterLab's scope?
- Any existing extensions I should build upon?
- Preferred approach for server-side AI processing?
- Suggestions for integration points?
```

1. **Identify Active Maintainers**: Review recent PRs to identify 2-3 active maintainers who review extensions. Study their feedback patterns to understand their preferences.
2. **Optional: Small Contribution**: Consider making a small, non-critical contribution (e.g., fixing a typo in docs, improving an error message) to familiarize yourself with the review process.

**Deliverable**: Positive engagement with the community, feedback on your RFC, and relationships with key maintainers.

---

## Stage 1: Feature 1 - The Academic Research Library & Discovery Engine

**Status**: ✅ **Complete** - All core features implemented and functional.

**Objective**: To build a robust, end-to-end JupyterLab extension that allows researchers to **discover, import, manage, and search** a local library of academic papers. This stage focuses on creating a seamless workflow from discovery via academic APIs to a searchable, enriched metadata database, with specific affordances for learning science research built-in from the start.

### Phase 1.1: Backend - Discovery, Processing, and Metadata Service

**Actual Directory Structure (`jupyterlab_research_assistant_wwc_copilot/`)**:

```
jupyterlab_research_assistant_wwc_copilot/  # Python package (underscores)
├── __init__.py                              # Server extension entry point
├── routes.py                                # API handlers (all in one file initially)
├── services/                                 # Business logic
│   ├── __init__.py
│   ├── semantic_scholar.py                  # API client for Semantic Scholar
│   ├── ai_extractor.py                      # AI metadata extraction
│   ├── pdf_parser.py                        # Text extraction with PyMuPDF
│   └── db_manager.py                       # Database session management
├── database/                                # Database setup
│   ├── __init__.py
│   ├── models.py                            # SQLAlchemy ORM models
│   └── migrations/                          # Alembic database migrations (future)
└── tests/
    ├── __init__.py
    ├── test_routes.py
    ├── test_services.py
    └── test_integration.py
```

This phase establishes the server-side foundation. It will be a JupyterLab server extension written in Python, responsible for querying external APIs, handling file uploads, parsing PDFs, extracting metadata, and managing the database.

**Key Components & Technologies**:

1. **Academic Discovery Service**:
    - **Primary Tool**: **Semantic Scholar API**. This provides free, high-quality access to a massive academic graph, including search, paper details, and citation networks [3].
    - **Implementation**: A Python client will be created to handle requests to the Semantic Scholar API. This service will power the frontend's discovery features.
    - **Code Example (`backend/services/semantic_scholar.py`)**:

      ```python
      # File: jupyterlab_research_assistant_wwc_copilot/services/semantic_scholar.py
      import requests
      from typing import List, Dict, Optional
      import time

      class SemanticScholarAPI:
          BASE_URL = "https://api.semanticscholar.org/graph/v1"

          def __init__(self, api_key: Optional[str] = None):
              self.session = requests.Session()
              if api_key:
                  self.session.headers.update({"x-api-key": api_key})
              self.last_request_time = 0
              self.min_request_interval = 0.3  # Rate limiting

          def _rate_limit(self):
              """Simple rate limiting to avoid hitting API limits."""
              current_time = time.time()
              time_since_last = current_time - self.last_request_time
              if time_since_last < self.min_request_interval:
                  time.sleep(self.min_request_interval - time_since_last)
              self.last_request_time = time.time()

          def search_papers(self, query: str, year: Optional[str] = None, limit: int = 20) -> Dict:
              """Search for papers using a query and optional year range."""
              self._rate_limit()
              params = {
                  "query": query,
                  "limit": min(limit, 100),  # API max is 100
                  "fields": "title,authors,year,abstract,doi,openAccessPdf,paperId,citationCount"
              }
              if year:
                  params["year"] = year
              response = self.session.get(f"{self.BASE_URL}/paper/search", params=params, timeout=10)
              response.raise_for_status()
              data = response.json()
              return {"data": data.get("data", []), "total": data.get("total", 0)}

          def get_paper_details(self, paper_id: str) -> Optional[Dict]:
              """Fetch detailed information for a single paper by Semantic Scholar ID."""
              self._rate_limit()
              params = {"fields": "title,authors,year,abstract,doi,openAccessPdf,paperId,citationCount"}
              response = self.session.get(f"{self.BASE_URL}/paper/{paper_id}", params=params, timeout=10)
              if response.status_code == 404:
                  return None
              response.raise_for_status()
              return response.json()
      ```

2. **PDF Text and Basic Metadata Extraction**:
    - **Primary Tool**: **PyMuPDF (`fitz`)** will be used for its high speed and accuracy in extracting raw text and basic metadata (e.g., title, author from PDF properties) [4].
    - **Implementation**: A Python function will open an uploaded or downloaded PDF, iterate through pages to extract the full text, and retrieve the document's built-in metadata dictionary.

3. **AI-Powered Deep Metadata Extraction**:
    This is the core intelligent feature for enriching papers beyond what standard APIs provide. The extracted text will be processed by a language model to identify and structure detailed academic metadata, especially for the WWC Co-Pilot.
    - **Alternative A (High-Quality Cloud API)**: **Claude 3** or **GPT-4.1**. Highest accuracy, but requires API keys and internet.
    - **Alternative B (Local/Open-Source LLM)**: **Ollama** with `Llama-3-8B` or `Mistral-7B`. Excellent for privacy, no cost, but requires more powerful hardware.
    - **Alternative C (Specialized Non-LLM Tools)**: **GROBID**. Very fast for standard bibliographic data, but less flexible for custom learning science fields.

    **Recommended Path**: Implement support for **Alternative A** and **Alternative B**, allowing the user to choose their preferred method in the settings.
    - **Code Example (`jupyterlab_research_assistant_wwc_copilot/services/ai_extractor.py`)**:

      ```python
      from openai import OpenAI # Works for both OpenAI and Anthropic-compatible APIs
      import json

      class AIExtractor:
          def __init__(self, client: OpenAI, model: str):
              self.client = client
              self.model = model

          def extract_metadata(self, text: str, schema: Dict) -> Dict:
              """Extracts metadata from text based on a JSON schema."""
              prompt = f"""Please extract the following information from the provided academic paper text. Respond with a single, valid JSON object that conforms to the schema.

              Schema: {json.dumps(schema, indent=2)}

              Paper Text:
              {text[:16000]} # Truncate for context window
              """

              response = self.client.chat.completions.create(
                  model=self.model,
                  messages=[{"role": "user", "content": prompt}],
                  response_format={"type": "json_object"}
              )
              try:
                  return json.loads(response.choices[0].message.content)
              except (json.JSONDecodeError, IndexError):
                  return {}
      ```

4. **Database Storage**:
    - **Technology**: **SQLite** via **SQLAlchemy**. This provides a robust, file-based database with a proper ORM for maintainable queries.
    - **Schema**: The schema is expanded to include data from Semantic Scholar and fields necessary for the WWC Co-Pilot.

    _Table 1: Expanded Database Schema_

    | Table Name | Column Name | Data Type | Description |
    | --------------------------- | --------------------- | --------- | ------------------------------------------------ |
    | `papers` | `id` | INTEGER | Primary Key |
    | | `title` | TEXT | The title of the paper. |
    | | `authors` | TEXT | JSON array of author names. |
    | | `year` | INTEGER | Publication year. |
    | | `doi` | TEXT | Digital Object Identifier. |
    | | `s2_id` | TEXT | Semantic Scholar ID for citation graph lookups. |
    | | `citation_count` | INTEGER | Number of citations. |
    | | `pdf_path` | TEXT | Filesystem path to the stored PDF. |
    | `study_metadata` | `paper_id` | INTEGER | Foreign key to `papers.id`. |
    | | `methodology` | TEXT | e.g., "RCT", "Quasi-experimental". |
    | | `sample_size_baseline`| INTEGER | N at baseline (for WWC). |
    | | `sample_size_endline` | INTEGER | N at endline (for WWC). |
    | | `effect_sizes` | TEXT | JSON object of reported effect sizes. |
    | `learning_science_metadata` | `paper_id` | INTEGER | Foreign key to `papers.id`. |
    | | `learning_domain` | TEXT | e.g., "Cognitive", "Affective". |
    | | `intervention_type` | TEXT | e.g., "Spaced Repetition", "Active Learning". |

### Phase 1.2: Frontend - The Research Library Panel

**Actual Directory Structure (`src/`)**:

```typescript
src/
├── index.ts                  // Extension entry point and plugin definition
├── request.ts                // API request helper (already exists)
├── api.ts                    // Typed API client functions
├── widgets/                  // React components
│   ├── ResearchLibraryPanel.tsx  // Main sidebar panel
│   ├── DiscoveryTab.tsx      // Search UI for Semantic Scholar
│   ├── LibraryTab.tsx        // View for local library
│   ├── PaperCard.tsx         // Component for a single paper
│   └── DetailView.tsx        // Detailed view of a paper's metadata
├── commands.ts               // Command palette definitions (optional, can be in index.ts)
└── __tests__/
    └── *.spec.tsx            // Component tests
```

This phase focuses on building the user-facing interface as a new panel in the JupyterLab sidebar, using TypeScript and React.

**Key UI/UX Components**:

1. **Main Panel**: A new sidebar panel, registered with a custom icon, that serves as the main view for the research library.
2. **Discovery & Import Tab**: The default view, allowing users to find new papers.
    - **UI Mockup**: A search bar, filters for year and open access, and a results list.
    - **Code Example (`src/widgets/DiscoveryTab.tsx`)**:

      ```typescript
      import React, { useState } from 'react';
      import { api } from '../services/api';

      interface PaperResult {
        paperId: string;
        title: string;
        authors: { name: string }[];
        year: number;
        abstract: string;
      }

      export const DiscoveryTab = (): JSX.Element => {
        const [query, setQuery] = useState('');
        const [results, setResults] = useState<PaperResult[]>([]);
        const [isLoading, setIsLoading] = useState(false);

        const handleSearch = async () => {
          if (!query) return;
          setIsLoading(true);
          const papers = await api.searchSemanticScholar(query);
          setResults(papers);
          setIsLoading(false);
        };

        const handleImport = async (paper: PaperResult) => {
          await api.importPaper(paper.paperId, paper.doi);
          // Optionally show a notification
        };

        return (
          <div>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search Semantic Scholar..."
            />
            <button onClick={handleSearch} disabled={isLoading}>
              {isLoading ? 'Searching...' : 'Search'}
            </button>
            <div>
              {results.map(paper => (
                <div key={paper.paperId} className="paper-card">
                  <h3>{paper.title} ({paper.year})</h3>
                  <p>{paper.authors.map(a => a.name).join(', ')}</p>
                  <p>{paper.abstract}</p>
                  <button onClick={() => handleImport(paper)}>Import</button>
                </div>
              ))}
            </div>
          </div>
        );
      };
      ```

3. **Library Tab**: A tab to view and search the papers already imported into the local database.
4. **Paper Detail View**: A dedicated view that displays all extracted metadata for a selected paper, including the learning science-specific fields and a button to open the original PDF.

### Phase 1.3: Integration & Command System

This phase focuses on integrating the extension into JupyterLab's command system, menus, and keyboard shortcuts.

**Integration Points**:

1. **Plugin Registration**: Register the extension with JupyterLab's plugin system using the `JupyterFrontEndPlugin` interface.
2. **Command Palette**: Add commands to the command palette for quick access:
    - `jupyterlab-research-assistant-wwc-copilot:open-library` - Open the research library panel
    - `jupyterlab-research-assistant-wwc-copilot:import-pdf` - Open file picker to import a local PDF
    - `jupyterlab-research-assistant-wwc-copilot:export-library` - Export library as CSV/JSON
3. **Main Menu Integration**: Add a "Research" menu to the main menu bar with the above commands.
4. **Keyboard Shortcuts**: Register keyboard shortcuts for frequently used commands (e.g., `Ctrl+Shift+R` for search).
5. **File Browser Context Menu**: Add a "Import to Research Library" option when right-clicking PDF files in the file browser.

**Code Example (`src/index.ts` - plugin registration)**:

```typescript
// In src/index.ts
import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
import { ICommandPalette } from '@jupyterlab/apputils';
import { ResearchLibraryPanel } from './widgets/ResearchLibraryPanel';

const PLUGIN_ID = 'jupyterlab-research-assistant-wwc-copilot:plugin';

const plugin: JupyterFrontEndPlugin<void> = {
  id: PLUGIN_ID,
  autoStart: true,
  optional: [ICommandPalette],
  activate: (app: JupyterFrontEnd, palette: ICommandPalette | null) => {
    // Create panel
    const panel = new ResearchLibraryPanel();
    app.shell.add(panel, 'left', { rank: 300 });

    // Register command
    app.commands.addCommand('jupyterlab-research-assistant-wwc-copilot:open-library', {
      label: 'Open Research Library',
      execute: () => {
        app.shell.activateById(panel.id);
      }
    });

    // Add to palette
    if (palette) {
      palette.addItem({
        command: 'jupyterlab-research-assistant-wwc-copilot:open-library',
        category: 'Research Assistant'
      });
    }
  }
};

export default plugin;
```

### Phase 1.4: Testing & Documentation

**Testing Strategy**:

1. **Unit Tests**: Write tests for all backend functions (PDF parsing, metadata extraction, database queries) and frontend components (search bar, paper cards, detail view).
2. **Integration Tests**: Test the full workflow from search to import to database storage.
3. **Performance Benchmarks**: Measure and document extraction time for papers of various lengths.
4. **Edge Cases**:
    - **Malformed PDFs**: Handle corrupted or unreadable PDFs gracefully.
    - **API Rate Limits**: Implement exponential backoff for Semantic Scholar and AI APIs.
    - **Large Libraries**: Test performance with 1,000+ papers in the database.
    - **Concurrent Uploads**: Ensure multiple simultaneous uploads don't corrupt the database.
    - **No Open Access PDF**: Handle cases where Semantic Scholar finds a paper but no downloadable PDF.
    - **Empty/Irrelevant Text**: What happens if the extracted text is garbage or from a non-academic document?
    - **Network Failures**: Handle failed API calls gracefully.

**Documentation Requirements**:

1. **User Guide**: A comprehensive guide with screenshots showing how to search, import, and manage papers.
2. **API Documentation**: Document all backend endpoints with request/response examples.
3. **Architecture Diagram**: A visual representation of the system components and data flow.
4. **Configuration Guide**: Instructions for setting up API keys for Claude, OpenAI, or Ollama.

---

## Stage 2: Feature 2 - The WWC Co-Pilot & Synthesis Engine

**Status**: ✅ **Complete** - All Stage 2 features are implemented, including core features (WWC assessment, meta-analysis, conflict detection) and enhancements (enhanced WWC UI, subgroup analysis, publication bias assessment, advanced conflict detection, sensitivity analysis).

**Objective**: To build an advanced feature that allows researchers to select multiple studies from their library, perform a rigorous, semi-automated WWC quality assessment, and generate a preliminary synthesis, including a meta-analysis and conflict detection.

### Phase 2.1: Backend - The WWC & Synthesis Service

**Directory Structure (add to `jupyterlab_research_assistant_wwc_copilot/`)**:

```
├── handlers/
│   ├── wwc.py              # WWC assessment endpoint
│   ├── meta_analysis.py    # Meta-analysis endpoint
│   └── conflict.py         # Conflict detection endpoint
├── services/
│   ├── wwc_assessor.py     # Core WWC logic
│   ├── meta_analyzer.py    # Statsmodels meta-analysis
│   ├── visualizer.py       # Forest plot generation
│   └── conflict_detector.py  # NLI conflict detection
└── tests/
    ├── test_wwc_assessor.py
    └── test_meta_analyzer.py
```

This phase extends the backend server extension with new API endpoints and business logic for quality assessment and study synthesis.

**Key Components & Technologies**:

1. **WWC Quality Assessment Engine**:
    - **The Core Logic**: This is the heart of the WWC Co-Pilot. It implements the decision rules from the WWC Handbook v5.0 as a series of functions.
    - **Implementation**: A Python class will take in study metadata (extracted in Stage 1) and user judgments to produce a full WWC assessment.
    - **Code Example (`jupyterlab_research_assistant_wwc_copilot/services/wwc_assessor.py`)**: This is the detailed implementation from our research, showing how the handbook's rules are translated into code.

      ```python
      from dataclasses import dataclass, field
      from typing import Optional, Dict, List
      from enum import Enum

      class WWCRating(Enum):
          MEETS_WITHOUT_RESERVATIONS = "Meets WWC Standards Without Reservations"
          MEETS_WITH_RESERVATIONS = "Meets WWC Standards With Reservations"
          DOES_NOT_MEET = "Does Not Meet WWC Standards"

      class AttritionBoundary(Enum):
          OPTIMISTIC = "optimistic"
          CAUTIOUS = "cautious"

      @dataclass
      class WWCAssessment:
          # --- Fields requiring human judgment ---
          chosen_attrition_boundary: AttritionBoundary = AttritionBoundary.CAUTIOUS
          adjustment_strategy_is_valid: Optional[bool] = None

          # --- Fields for automated extraction & calculation ---
          is_rct: bool = True
          randomization_documented: bool = False
          overall_attrition: Optional[float] = None
          differential_attrition: Optional[float] = None
          is_high_attrition: Optional[bool] = None
          baseline_effect_size: Optional[float] = None
          baseline_equivalence_satisfied: Optional[bool] = None

          # --- Final Rating ---
          final_rating: WWCRating = WWCRating.DOES_NOT_MEET
          rating_justification: List[str] = field(default_factory=list)

      class WWCQualityAssessor:
          ATTRITION_BOUNDARIES = {
              "cautious": {0.10: 0.05, 0.20: 0.03, 0.30: 0.01, 0.40: 0.00},
              "optimistic": {0.10: 0.07, 0.20: 0.05, 0.30: 0.03, 0.40: 0.01}
          }

          def is_low_attrition(self, overall: float, differential: float, boundary: AttritionBoundary) -> bool:
              if overall is None or differential is None: return False
              boundary_table = self.ATTRITION_BOUNDARIES[boundary.value]
              for overall_threshold, diff_threshold in sorted(boundary_table.items()):
                  if overall <= overall_threshold:
                      return differential <= diff_threshold
              return False

          def assess(self, extracted_data: Dict, user_judgments: Dict) -> WWCAssessment:
              assessment = WWCAssessment(**user_judgments)
              assessment.rating_justification = []

              if not extracted_data.get("randomization_documented"):
                  assessment.final_rating = WWCRating.DOES_NOT_MEET
                  assessment.rating_justification.append("Randomization was not documented.")
                  return assessment

              assessment.overall_attrition = (extracted_data["baseline_n"] - extracted_data["endline_n"]) / extracted_data["baseline_n"]
              assessment.differential_attrition = abs(extracted_data["treatment_attrition"] - extracted_data["control_attrition"])

              assessment.is_high_attrition = not self.is_low_attrition(
                  assessment.overall_attrition,
                  assessment.differential_attrition,
                  assessment.chosen_attrition_boundary
              )

              requires_baseline_check = not assessment.is_rct or assessment.is_high_attrition
              if requires_baseline_check:
                  # ... baseline equivalence logic ...
                  pass

              if not assessment.is_high_attrition:
                  assessment.final_rating = WWCRating.MEETS_WITHOUT_RESERVATIONS
              elif assessment.is_high_attrition and assessment.baseline_equivalence_satisfied:
                  assessment.final_rating = WWCRating.MEETS_WITH_RESERVATIONS

              return assessment
      ```

2. **Meta-Analysis Engine**:
    - **Primary Tool**: The **`statsmodels`** library in Python will be used for its robust and well-validated meta-analysis capabilities [5].
    - **Implementation**: An API endpoint will accept a list of paper IDs. The service will retrieve the relevant study metadata (effect sizes, standard errors, sample sizes) from the database and use `statsmodels.stats.meta_analysis` to perform a random-effects meta-analysis.

3. **Forest Plot Generation**:
    - **Primary Tool**: **`matplotlib`** will be used to generate a classic forest plot.
    - **Implementation**: The backend will generate the plot as a PNG or SVG image and send it to the frontend for display.
    - **Code Example (`jupyterlab_research_assistant_wwc_copilot/services/visualizer.py`)**:

      ```python
      import matplotlib.pyplot as plt
      import statsmodels.stats.meta_analysis as meta
      import io
      import base64

      class Visualizer:
          def create_forest_plot(self, effect_sizes, std_errs, labels):
              """Generates a forest plot and returns it as a base64 encoded string."""
              fig, ax = plt.subplots(figsize=(8, 5), dpi=100)
              meta.forest_plot(effect_sizes, std_errs, labels=labels, ax=ax)
              ax.set_title("Forest Plot of Study Effect Sizes")

              buf = io.BytesIO()
              fig.savefig(buf, format=\"png\", bbox_inches=\"tight\")
              plt.close(fig)

              return base64.b64encode(buf.getvalue()).decode("utf-8")
      ```

4. **Conflict & Contradiction Detection**:
    - **Approach**: Use a pre-trained **Natural Language Inference (NLI)** model to compare key findings extracted from papers.
    - **Implementation**: Key findings will be paired up and fed into an NLI model (e.g., a DeBERTa or RoBERTa model fine-tuned on an NLI dataset like MNLI). Pairs classified as `contradiction` will be flagged.

### Phase 2.2: Frontend - The Synthesis Workbench

This phase builds the UI for the synthesis engine, likely as a new main area widget in JupyterLab that opens when a user initiates a comparison.

**Key UI/UX Components**:

1. **Study Selection**: The research library panel will be updated to allow multi-select, with a "Synthesize Studies" button appearing when two or more papers are selected.
2. **WWC Co-Pilot Interface**: A dedicated view for a single paper that walks the user through the WWC assessment.
    - **UI Mockup**: A multi-step form with clear sections for Attrition, Baseline Equivalence, etc. It will use the data extracted in Stage 1 to pre-fill fields and show initial calculations.
    - **Code Example (`src/widgets/WWCCoPilot.tsx`)**:

      ```typescript
      import React, { useState, useEffect } from 'react';
      import { api } from '../services/api';

      export const WWCCoPilot = ({ paperId }) => {
        const [assessment, setAssessment] = useState(null);
        const [judgments, setJudgments] = useState({ chosen_attrition_boundary: 'cautious' });

        useEffect(() => {
          const runAssessment = async () => {
            const result = await api.runWWCAssessment(paperId, judgments);
            setAssessment(result);
          };
          runAssessment();
        }, [paperId, judgments]);

        return (
          <div>
            <h2>WWC Co-Pilot for {assessment?.paper_title}</h2>

            <div className="assessment-section">
              <h3>Attrition</h3>
              <p>Overall: {assessment?.overall_attrition?.toFixed(2)}%</p>
              <p>Differential: {assessment?.differential_attrition?.toFixed(2)}%</p>
              <select
                value={judgments.chosen_attrition_boundary}
                onChange={e => setJudgments({...judgments, chosen_attrition_boundary: e.target.value})}
              >
                <option value="cautious">Cautious Boundary</option>
                <option value="optimistic">Optimistic Boundary</option>
              </select>
              <p>Status: {assessment?.is_high_attrition ? 'High Attrition' : 'Low Attrition'}</p>
            </div>

            {/* ... other sections for baseline equivalence, etc. ... */}

            <div className="final-rating">
              <h3>Final Rating: {assessment?.final_rating}</h3>
              <ul>
                {assessment?.rating_justification.map(reason => <li key={reason}>{reason}</li>)}
              </ul>
            </div>
          </div>
        );
      };
      ```

3. **Synthesis Dashboard**: A dashboard view that presents the results of the backend analysis for multiple papers:
    - **Meta-Analysis Summary**: A clear, concise summary of the pooled effect size and confidence interval.
    - **Forest Plot Display**: The generated forest plot image will be displayed prominently.
    - **Conflict List**: A list of potential contradictions identified by the NLI model.
4. **Export Functionality**: Buttons to export the comparison matrix as a CSV and the synthesis dashboard as a Markdown report.

---

## Stage 3: Finalization, Documentation & Submission

**Objective**: To polish the features, write comprehensive documentation, and prepare the contribution for submission to the JupyterLab project, following all community guidelines.

### Phase 3.1: Testing & Refinement

- **Unit Tests**: Write comprehensive unit tests for all backend Python functions and frontend TypeScript/React components.
- **Integration Tests**: Create integration tests for the full workflow, from PDF upload to synthesis generation.
- **User Feedback**: Solicit feedback from potential users (e.g., other researchers) to identify usability issues and areas for improvement.

### Phase 3.2: Documentation

- **User Guide**: Write a clear, user-facing guide on how to use the new features, with screenshots and examples, focusing on the WWC Co-Pilot workflow.
- **Developer Docs**: Document the architecture, API endpoints, and key code components to help future developers understand and extend the work.
- **Changelog**: Create a detailed entry for the project's changelog, summarizing the new features and improvements.

### Phase 3.3: Publishing Preparation

- **Code Cleanup**: Ensure all code adheres to JupyterLab's coding style and linting rules.
- **Package Metadata**: Verify that `package.json` and `pyproject.toml` have correct and complete metadata (version, author, license, keywords, repository URL).
- **README**: Write a comprehensive README with installation instructions, usage examples, screenshots, and links to documentation.

### Phase 3.4: Video Presentation & Community Outreach

**Video Production Checklist**:

- [ ] Write a detailed script for a 7-10 minute video.
- [ ] Record screen demos for each feature (multiple takes).
- [ ] Record a clear voiceover or narrate live.
- [ ] Edit the video to cut mistakes and add transitions.
- [ ] Add captions for accessibility.
- [ ] Export at 1080p and upload to YouTube (public or unlisted).

**Demo Tips**:

- **Use Clean Test Data**: Don't use messy, real-world data for demos.
- **Pre-Generate Results**: Have synthesis results ready to show for a smooth demo.
- **Cursor Highlighting**: Use a tool to highlight your cursor during code walkthroughs.
- **Zoom In**: Zoom in on important code sections or UI elements.

**Community Outreach**:

- Post about your extension on the JupyterLab Discourse forum.
- Share on relevant social media (Twitter/X, LinkedIn, Reddit's r/JupyterLab).
- Consider writing a blog post explaining the motivation and design decisions.

### Phase 3.5: Final Polish & Publishing

**Pre-Publishing Quality Assurance Checklist**:

- [ ] All tests pass locally and on CI (if you set up GitHub Actions).
- [ ] Code coverage >80%.
- [ ] Linting passes with no warnings.
- [ ] Documentation is complete and accurate.
- [ ] Screenshots in docs are up-to-date.
- [ ] Example notebooks run without errors.
- [ ] Performance is acceptable (no major lag with 100+ papers).
- [ ] Accessibility tested (keyboard navigation works).

**Publishing Steps**:

1. **Publish to npm**: `npm publish` (for the frontend package)
2. **Publish to PyPI**: `python -m build && twine upload dist/*` (for the Python package)
3. **Submit to JupyterLab Extension Registry**: Follow the [extension listing process](https://jupyterlab.readthedocs.io/en/stable/extension/extension_tutorial.html#publishing-your-extension) to list your extension
4. **Create GitHub Release**: Tag a release on GitHub with release notes
5. **Share Widely**: Post announcement on Discourse, social media, and relevant mailing lists

---

## Appendix A: AI Provider Configuration

To accommodate the different alternatives for AI-powered extraction, the extension will be configurable via JupyterLab's advanced settings system. This allows users to choose their preferred provider and enter API keys without modifying the code.

**Configuration in JupyterLab Settings**:

Users will be able to configure their preferred extraction method in JupyterLab's settings UI:

```json
{
  "wwc-co-pilot": {
    "extraction_provider": "claude", // "claude", "openai", or "ollama"
    "api_key": "sk-...", // For Claude or OpenAI
    "ollama_model": "llama3", // For local Ollama instances
    "ollama_url": "http://localhost:11434"
  }
}
```

---

## Appendix B: Learning Science & WWC Focus

To ensure the tool is particularly useful for learning science research, the following specific features will be built-in from the start:

1. **Specialized Metadata Schema**: The database schema (Table 1) includes fields like `learning_domain` and `intervention_type`, which are critical for organizing and comparing learning science studies.
2. **Preset Extraction Templates**: The AI extraction prompt will include a preset template specifically for learning science and WWC criteria. It will instruct the model to look for:
    - **Learning Objectives**: What were the students supposed to learn?
    - **Intervention Components**: What specific techniques were used (e.g., worked examples, feedback, collaboration)?
    - **WWC Criteria**: Baseline/endline sample sizes, attrition numbers for treatment/control, and baseline demographic tables.
3. **Example Workflows**: The user documentation will include a tutorial specifically for learning scientists, demonstrating how to import a set of papers on a topic like "spaced repetition" and generate a meta-analytic summary with WWC quality ratings.

---

## Appendix C: Success Criteria

### For JupyterLab Contribution

- [ ] Both PRs follow contribution guidelines exactly
- [ ] Code matches JupyterLab style and patterns
- [ ] Tests are comprehensive and passing
- [ ] Documentation is clear and complete
- [ ] Maintainers engage with PRs (questions/feedback)
- [ ] Features are genuinely useful to the research community

### For Learning Science Goals

- [ ] Tools are useful for Alpha School research evaluation
- [ ] Learning science preset demonstrates deep domain knowledge
- [ ] Quality indicators align with ed research standards (WWC)
- [ ] Statistical methods are appropriate for education meta-analysis
- [ ] Example workflows showcase real use cases

---

## Appendix D: Key Resources

### JupyterLab Documentation

- **Main docs**: <https://jupyterlab.readthedocs.io/>
- **Extension tutorial**: <https://jupyterlab.readthedocs.io/en/stable/extension/extension_tutorial.html>
- **Contributing guide**: <https://github.com/jupyterlab/jupyterlab/blob/main/CONTRIBUTING.md>
- **Architecture**: See the [JupyterLab documentation](https://jupyterlab.readthedocs.io/) for architecture details

### JupyterLab Community

- **Matrix/Element chat**: <https://matrix.to/#/#jupyterlab:matrix.org>
- **Discourse forum**: <https://discourse.jupyter.org/>
- **GitHub discussions**: <https://github.com/jupyterlab/jupyterlab/discussions>

### Learning Science Resources

- **What Works Clearinghouse**: <https://ies.ed.gov/ncee/wwc/>
- **Campbell Collaboration**: <https://www.campbellcollaboration.org/>
- **GRADE handbook**: <https://gdt.gradepro.org/app/handbook/handbook.html>
- **Cochrane Handbook**: Search for "Cochrane handbook" to find the latest version

### Statistical Tools

- **Meta-analysis in Python (statsmodels)**: <https://www.statsmodels.org/stable/stats.html#meta-analysis>
- **R metafor package**: <https://www.metafor-project.org/>
- **Effect size calculators**: <https://www.psychometrica.de/effect_size.html>

---

## Appendix E: Notes & Reminders

### Speed vs Quality

- Build fast, but don't skip testing or documentation.
- Use AI to accelerate development, but review all generated code.
- Don't reinvent the wheel—use existing libraries like `statsmodels` and `PyMuPDF`.

### Community Engagement

- Over-communicate with maintainers.
- Be responsive to feedback.
- Acknowledge when you're wrong.
- Thank people for their time.
- Build relationships, not just code.

### Learning Science Focus

- Every feature should have a learning science application in mind.
- The preset is the showcase, but the core tools must be general.
- The Alpha School use case drives design decisions.
- Document pedagogical reasoning in addition to technical details.

### Deliverable Priority

1. **Working, tested code** ← MOST IMPORTANT
2. **Clear documentation**
3. **Professional PRs**
4. **Video walkthrough**
5. **Bonus materials**

---

## Appendix F: Success Criteria & Timeline

### Success Criteria

- **Functionality**: Both the Research Library and WWC Co-Pilot/Synthesis Engine features are fully implemented and functional.
- **Usability**: A researcher can successfully discover, import, assess with the WWC Co-Pilot, and synthesize a set of papers, all within the JupyterLab interface.
- **Alignment**: The final code contribution adheres to all JupyterLab community guidelines for code style, testing, and documentation.
- **Performance**: PDF processing and metadata extraction for a typical 15-page paper completes in under 60 seconds.

### Estimated Timeline (8-12 Weeks)

- **Weeks 1-2**: Stage 0 - Foundation & Repository Mastery.
- **Weeks 3-5**: Stage 1 - Research Library & Discovery Engine (Backend & Frontend).
- **Weeks 6-8**: Stage 2 - WWC Co-Pilot & Synthesis Engine (Backend & Frontend).
- **Weeks 9-10**: Stage 3 - Testing, Refinement, and Documentation.
- **Weeks 11-12**: Stage 3 - Submission Preparation and Pull Request Management.

---

## Appendix D: Learning Science Preset & Templates

### Overview

The Learning Science Preset is a specialized configuration that optimizes the tool for education research. It includes pre-configured extraction templates, quality indicators, and outcome measures specific to learning science.

### Statistical Considerations for Learning Science

**Common Effect Sizes in Education**:

- **Cohen's d**: Standardized mean difference between two groups.
- **Hedge's g**: A variation of Cohen's d, corrected for small sample sizes.
- **Odds Ratios**: For binary outcomes (e.g., pass/fail, dropout/stay).
- **Correlation Coefficients (r)**: For relationships between continuous variables.

**Meta-Analysis Methods**:

- **Random-Effects Models**: The default for education research, as it assumes that the true effect size varies from study to study.
- **Subgroup Analysis**: To explore moderators (e.g., does the intervention work better for younger students?).
- **Meta-Regression**: To analyze the relationship between study characteristics and effect sizes.
- **Publication Bias Assessment**: Using techniques like funnel plots and Egger's test to check for missing studies.

### Intervention & Outcome Taxonomies

**Intervention Taxonomy**:

- **Instructional Strategies**: Direct instruction, inquiry-based learning, project-based learning, etc.
- **Technology Integration**: Intelligent tutoring systems, educational games, online simulations, etc.
- **Assessment/Feedback**: Formative vs. summative, immediate vs. delayed feedback, peer vs. instructor feedback.
- **Collaborative Learning**: Think-pair-share, jigsaw, peer instruction, etc.
- **Self-Regulated Learning**: Goal setting, metacognitive prompts, self-monitoring, etc.

**Outcome Measures Library**:

- **Standardized Tests**: SAT, GRE, PISA, TIMSS, etc.
- **Custom Assessments**: Pre/post tests, concept inventories, performance tasks.
- **Behavioral Measures**: Time on task, help-seeking behavior, dropout rates.
- **Affective Measures**: Surveys for engagement, motivation, self-efficacy, anxiety.
- **Retention/Transfer**: Measures of long-term knowledge retention and application to new contexts.

### Extraction Schema for Learning Science

The AI extraction prompt will use this schema when the learning science preset is active:

```json
{
  "learning_domain": {
    "type": "enum",
    "values": ["cognitive", "affective", "behavioral", "metacognitive"],
    "description": "Primary domain of learning targeted by the intervention"
  },
  "bloom_level": {
    "type": "enum",
    "values": [
      "remember",
      "understand",
      "apply",
      "analyze",
      "evaluate",
      "create"
    ],
    "description": "Highest Bloom's taxonomy level addressed"
  },
  "intervention_components": {
    "type": "array",
    "items": {
      "component": "string",
      "duration": "string",
      "frequency": "string"
    },
    "description": "Specific instructional techniques used"
  },
  "learning_outcome_types": {
    "type": "array",
    "values": [
      "knowledge_gain",
      "skill_acquisition",
      "attitude_change",
      "behavior_change"
    ],
    "description": "Types of learning outcomes measured"
  },
  "assessment_types": {
    "type": "array",
    "values": ["formative", "summative", "authentic", "standardized"],
    "description": "Types of assessments used"
  },
  "setting": {
    "type": "enum",
    "values": ["k12", "higher_ed", "corporate", "online", "hybrid"],
    "description": "Educational setting"
  },
  "wwc_criteria": {
    "baseline_n_treatment": "integer",
    "baseline_n_control": "integer",
    "endline_n_treatment": "integer",
    "endline_n_control": "integer",
    "randomization_method": "string",
    "baseline_equivalence_reported": "boolean"
  }
}
```

### Quality Indicators for Learning Science

The preset includes automated checks for common quality issues in education research:

```python
# backend/presets/learning_science_quality.py

class LearningScienceQualityAssessor:
    def assess(self, paper: Paper) -> QualityReport:
        """Assess quality of learning science research based on WWC standards."""
        report = QualityReport()

        # Check randomization
        if paper.methodology == "RCT":
            report.randomization = self.check_randomization(paper)

        # Check sample size adequacy (power analysis)
        report.sample_size = self.assess_power(paper)

        # Check outcome measure validity
        report.measures = self.assess_measures(paper)

        # Check attrition rates
        report.attrition = self.check_attrition(paper)

        # Implementation fidelity
        report.fidelity = self.check_fidelity(paper)

        # Overall WWC rating
        report.overall = self.calculate_wwc_rating(report)

        return report

    def check_randomization(self, paper: Paper) -> Dict:
        """Checks if randomization is properly documented."""
        keywords = ["random assignment", "randomized", "randomly assigned"]
        text = paper.full_text.lower()

        documented = any(kw in text for kw in keywords)
        method_described = "randomization method" in text or "random number" in text

        return {
            "documented": documented,
            "method_described": method_described,
            "rating": "adequate" if documented and method_described else "inadequate"
        }
```

### Example Workflows

The documentation will include these example notebooks:

**Example 1: Meta-Analysis of Spaced Repetition Studies**

```python
# Import the extension
from jupyterlab_research_assistant import ResearchLibrary, SynthesisEngine

# 1. Search for papers
library = ResearchLibrary()
library.search_semantic_scholar("spaced repetition learning", year="2015-2024")

# 2. Import relevant papers
library.import_selected(["paper_id_1", "paper_id_2", "paper_id_3"])

# 3. Filter to RCTs only
rcts = library.filter(methodology="RCT")

# 4. Run WWC assessment on each
for paper in rcts:
    assessment = library.run_wwc_assessment(paper.id)
    print(f"{paper.title}: {assessment.final_rating}")

# 5. Filter to high-quality studies
high_quality = [p for p in rcts if p.wwc_rating == "Meets Without Reservations"]

# 6. Run meta-analysis
engine = SynthesisEngine(preset="learning-science")
synthesis = engine.meta_analyze(high_quality, outcome="retention_test")

# 7. View results
synthesis.forest_plot()
print(f"Pooled effect: d = {synthesis.pooled_effect:.2f} [{synthesis.ci_lower:.2f}, {synthesis.ci_upper:.2f}]")

# 8. Export report
synthesis.export_report("spaced_repetition_meta_analysis.md")
```

---

## Appendix E: Detailed WWC Standards Implementation

### Understanding the WWC Handbook v5.0

The What Works Clearinghouse (WWC) provides a rigorous, systematic framework for assessing the quality of education research. The WWC Standards Handbook Version 5.0 [6] is not a vague set of guidelines—it is a detailed decision tree with specific numerical thresholds that make it ideal for software implementation.

### The Three-Tier Rating System

The WWC assigns one of three ratings to each study:

1. **Meets WWC Standards Without Reservations**: The gold standard. These are high-quality studies with low attrition, proper randomization, and minimal threats to validity.
2. **Meets WWC Standards With Reservations**: Acceptable quality studies that have some issues (e.g., high attrition) but compensate for them through statistical adjustments.
3. **Does Not Meet WWC Standards**: Studies with fatal flaws that make their findings unreliable.

### The Two-Boundary System for Attrition

Attrition (participant dropout) is the most critical and complex part of a WWC review. The handbook provides a clear, two-boundary system based on whether attrition is likely related to the intervention:

**Optimistic Boundary**: Used when the intervention is unlikely to influence who stays or leaves a study (e.g., a supplemental curriculum, a new textbook). This allows for slightly higher attrition rates.

**Cautious Boundary**: Used when the intervention could plausibly affect retention (e.g., a dropout prevention program, a school choice voucher, an intensive tutoring program). This is the default and more stringent boundary.

_Table 2: WWC Attrition Boundaries (from Handbook Appendix C)_

| Overall Attrition | Max Differential (Cautious) | Max Differential (Optimistic) |
|-------------------|----------------------------|-------------------------------|
| ≤ 10% | 5% | 7% |
| ≤ 20% | 3% | 5% |
| ≤ 30% | 1% | 3% |
| ≤ 40% | 0% | 1% |
| > 40% | Does Not Meet Standards | Does Not Meet Standards |

**Tooling Implication**: The WWC Co-Pilot must first ask the researcher to choose a boundary, providing the official WWC examples to guide their choice. This decision then dictates which set of thresholds to apply.

### Baseline Equivalence Standard

This standard is only required for certain study types: all quasi-experimental designs (QEDs), high-attrition RCTs, and compromised RCTs. The handbook provides a clear algorithm:

1. **Calculate the baseline difference** between treatment and control groups as a standardized effect size (Cohen's d).
2. **Compare this difference to specific thresholds**:
   - **≤ 0.05 SD**: Groups are considered equivalent. No statistical adjustment is required (but is recommended).
   - **> 0.05 SD and ≤ 0.25 SD**: An acceptable statistical adjustment (e.g., ANCOVA, regression with baseline as a covariate) _must_ be used.
   - **> 0.25 SD**: The study _Does Not Meet WWC Standards_.

**Tooling Implication**: The WWC Co-Pilot can automate this entirely. It will extract baseline means and standard deviations, calculate the effect size, and display the result against color-coded thresholds (green/yellow/red) to show the user exactly where the study stands.

### Implementation Fidelity

The WWC requires that the intervention be delivered as intended. The handbook specifies that reviewers should look for:

- **Quantitative measures** of fidelity (e.g., "Teachers implemented 85% of lessons").
- **Descriptions of monitoring procedures** (e.g., classroom observations, teacher logs).
- **Analysis of fidelity's relationship to outcomes** (e.g., did students whose teachers had higher fidelity have better outcomes?).

**Tooling Implication**: The WWC Co-Pilot will extract any mentions of "fidelity," "implementation," or "adherence" and present them to the researcher for judgment.

---

## Appendix E: Comprehensive Code Examples

### E.1: PDF Extraction with PyMuPDF

```python
# backend/extractors/pdf_parser.py
import fitz  # PyMuPDF
from typing import Dict, Optional

class PDFParser:
    def extract_text_and_metadata(self, pdf_path: str) -> Dict:
        """Extracts full text and built-in metadata from a PDF."""
        doc = fitz.open(pdf_path)

        # Extract metadata from PDF properties
        metadata = doc.metadata

        # Extract full text
        full_text = ""
        for page_num in range(len(doc)):
            page = doc[page_num]
            full_text += page.get_text()

        doc.close()

        return {
            "title": metadata.get("title", ""),
            "author": metadata.get("author", ""),
            "subject": metadata.get("subject", ""),
            "full_text": full_text,
            "page_count": len(doc)
        }
```

### E.2: Meta-Analysis with statsmodels

```python
# backend/services/meta_analyzer.py
import numpy as np
import statsmodels.stats.meta_analysis as meta
from typing import List, Dict

class MetaAnalyzer:
    def perform_random_effects_meta_analysis(self, studies: List[Dict]) -> Dict:
        """Performs a random-effects meta-analysis on a set of studies."""
        effect_sizes = np.array([s["effect_size"] for s in studies])
        std_errors = np.array([s["std_error"] for s in studies])

        # Perform random-effects meta-analysis
        result = meta.combine_effects(
            effect_sizes,
            std_errors,
            method_re="DL",  # DerSimonian-Laird estimator
            use_t=True
        )

        return {
            "pooled_effect": result.effect,
            "ci_lower": result.conf_int()[0],
            "ci_upper": result.conf_int()[1],
            "p_value": result.pvalue,
            "heterogeneity_i2": result.het_test().statistic,
            "heterogeneity_q": result.het_test().pvalue
        }
```

### E.3: Contradiction Detection with NLI

```python
# backend/services/conflict_detector.py
from transformers import pipeline
from typing import List, Dict

class ContradictionDetector:
    def __init__(self):
        self.nli_pipeline = pipeline(
            "text-classification",
            model="cross-encoder/nli-deberta-v3-base"
        )

    def find_contradictions(self, findings1: List[str], findings2: List[str]) -> List[Dict]:
        """Compares two lists of findings and returns any contradictions."""
        contradictions = []
        for f1 in findings1:
            for f2 in findings2:
                result = self.nli_pipeline(f"{f1} [SEP] {f2}")
                if result[0]["label"] == "contradiction" and result[0]["score"] > 0.8:
                    contradictions.append({
                        "finding1": f1,
                        "finding2": f2,
                        "confidence": result[0]["score"]
                    })
        return contradictions
```

### E.4: Backend API Endpoint Structure

```python
# backend/handlers/wwc_handler.py
from jupyter_server.base.handlers import APIHandler
import tornado
import json

class WWCAssessmentHandler(APIHandler):
    @tornado.web.authenticated
    def post(self):
        """Runs a WWC assessment for a given paper."""
        data = json.loads(self.request.body)
        paper_id = data.get("paper_id")
        user_judgments = data.get("judgments", {})

        # Fetch paper from database
        paper = self.db.get_paper(paper_id)

        # Extract relevant data
        extracted_data = {
            "randomization_documented": paper.randomization_method is not None,
            "baseline_n": paper.sample_size_baseline,
            "endline_n": paper.sample_size_endline,
            # ... more fields
        }

        # Run assessment
        assessor = WWCQualityAssessor()
        assessment = assessor.assess(extracted_data, user_judgments)

        self.finish(json.dumps(assessment.__dict__, default=str))
```

---

## Appendix F: Testing Strategy

### Unit Testing

Every backend function and frontend component must have comprehensive unit tests. The target is >80% code coverage.

**Backend Testing Example**:

```python
# backend/tests/test_wwc_assessor.py
import pytest
from services.wwc_assessor import WWCQualityAssessor, AttritionBoundary

def test_low_attrition_cautious_boundary():
    assessor = WWCQualityAssessor()
    result = assessor.is_low_attrition(
        overall=0.08,
        differential=0.04,
        boundary=AttritionBoundary.CAUTIOUS
    )
    assert result == True

def test_high_attrition_cautious_boundary():
    assessor = WWCQualityAssessor()
    result = assessor.is_low_attrition(
        overall=0.15,
        differential=0.06,
        boundary=AttritionBoundary.CAUTIOUS
    )
    assert result == False
```

**Frontend Testing Example**:

```typescript
// frontend/tests/DiscoveryTab.spec.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { DiscoveryTab } from '../widgets/DiscoveryTab';

test('search button triggers API call', async () => {
  render(<DiscoveryTab />);

  const input = screen.getByPlaceholderText('Search Semantic Scholar...');
  const button = screen.getByText('Search');

  fireEvent.change(input, { target: { value: 'spaced repetition' } });
  fireEvent.click(button);

  // Assert that loading state appears
  expect(screen.getByText('Searching...')).toBeInTheDocument();
});
```

### Integration Testing

Integration tests verify that the full workflow (from frontend action to backend processing to database storage) works correctly.

**Example Integration Test**:

```python
# backend/tests/test_integration.py
import pytest
from handlers.upload import UploadHandler
from database.models import Paper

@pytest.mark.integration
def test_pdf_upload_and_extraction_workflow(test_client, sample_pdf):
    # Upload a PDF
    response = test_client.post('/api/research/upload', files={'pdf': sample_pdf})
    assert response.status_code == 200
    paper_id = response.json()["paper_id"]

    # Verify paper was added to database
    paper = Paper.query.get(paper_id)
    assert paper is not None
    assert paper.title is not None
    assert len(paper.full_text) > 0
```

---

## Appendix G: Pull Request Templates

### PR #1: Research Library & Discovery Engine

```markdown
Title: Add Academic Research Library & Discovery Engine Extension

## Summary

This PR adds a JupyterLab extension for discovering, importing, and managing academic papers, enabling researchers to build a searchable research library without leaving JupyterLab.

## Motivation

Researchers using JupyterLab for data analysis currently lack integrated tools for managing the academic literature they reference. This extension fills that gap by providing:

- Discovery via Semantic Scholar API
- PDF import and metadata extraction
- Searchable local database
- Learning science-specific metadata fields

## Implementation

- **Backend**: Server extension for PDF processing, Semantic Scholar integration, and SQLite database management
- **Frontend**: Sidebar panel with discovery tab, library view, and paper detail view
- **AI Extraction**: Configurable support for Claude, GPT-4, or local Ollama models

## Features

- Search Semantic Scholar directly from JupyterLab
- Import PDFs via drag-and-drop or from search results
- Automatic metadata extraction (authors, year, methodology, sample sizes, etc.)
- Searchable library with filtering by methodology, year, learning domain
- Export to CSV/JSON/BibTeX
- Extensible template system for domain-specific metadata

## Testing

- 85% backend code coverage
- All UI components tested with Jest and React Testing Library
- Integration tests for full upload-extract-store workflow
- Performance benchmarks: <60s for 15-page paper extraction

## Documentation

- User guide with screenshots
- API documentation for all endpoints
- Architecture diagram
- Example notebooks demonstrating learning science use case

## Breaking Changes

None - this is a new extension.

## Checklist

- [x] Tests pass locally
- [x] Linting passes (ESLint, Prettier, Black, MyPy)
- [x] Documentation updated
- [x] Changelog updated
- [x] PR template filled out
```

### PR #2: WWC Co-Pilot & Synthesis Engine

```markdown
Title: Add WWC Co-Pilot & Study Synthesis Engine Extension

## Summary

Adds tools for assessing study quality using What Works Clearinghouse (WWC) standards and synthesizing findings across multiple papers, including meta-analysis and conflict detection.

## Motivation

Education researchers conducting systematic reviews need to:

1. Assess study quality using rigorous, standardized criteria (WWC)
2. Synthesize findings across studies
3. Identify contradictions in the literature

This extension provides semi-automated tools for all three tasks, scaffolding human judgment while automating tedious calculations.

## Implementation

- **WWC Assessment Engine**: Implements WWC Handbook v5.0 decision rules in Python
- **Meta-Analysis**: Uses statsmodels for random-effects meta-analysis
- **Forest Plots**: Generates publication-quality visualizations with matplotlib
- **Conflict Detection**: Uses NLI models to identify contradictory findings
- **Interactive UI**: Multi-step form that guides researchers through WWC assessment

## Features

- Semi-automated WWC quality assessment with human-in-the-loop
- Automatic attrition calculation with two-boundary system
- Baseline equivalence checking with color-coded thresholds
- Meta-analysis with heterogeneity statistics
- Forest plot generation
- Contradiction detection across studies
- Export synthesis reports as Markdown

## Dependencies

- Requires Research Library extension (PR #XXXX)
- Uses statsmodels, matplotlib, transformers
- Optional: Hugging Face model for NLI

## Testing

- Statistical calculations verified against R's metafor package
- 82% code coverage
- UI components tested
- End-to-end synthesis workflow tested with sample papers

## Documentation

- User guide with WWC assessment walkthrough
- Statistical methods documented
- WWC Handbook v5.0 implementation notes
- Architecture diagram
- API reference

## Checklist

- [x] Tests pass locally
- [x] Linting passes
- [x] Documentation updated
- [x] Changelog updated
```

---

## References

[1] JupyterLab Developer Documentation. (2024). _JupyterLab_. Retrieved from <https://jupyterlab.readthedocs.io/en/stable/extension/extension_dev.html>

[2] JupyterLab Contribution Guide. (2024). _JupyterLab GitHub_. Retrieved from <https://github.com/jupyterlab/jupyterlab/blob/master/CONTRIBUTING.md>

[3### Command & Server Extension Examples

This section provides two code snippets demonstrating how the frontend (TypeScript) and backend (Python) work together in a JupyterLab extension. The frontend registers a command that, when executed, calls an API endpoint provided by the backend.

#### How They Connect

1. **Frontend calls**: `${baseUrl}my-extension/hello`
2. **Backend handles**: The route registered at `url_path_join(base_url, "my-extension", "hello")`
3. **Backend responds**: JSON with a message
4. **Frontend displays**: The message in a dialog box

#### Key Takeaways

- **Commands are frontend-only**: They live in TypeScript.
- **API handlers are backend-only**: They live in Python.
- **They communicate via HTTP**: Using Jupyter Server's built-in authentication.
- **Both are required**: For features that need server-side processing.

This is the exact pattern you'll use for your WWC Co-Pilot features: frontend UI + backend processing (PDF extraction, database queries, meta-analysis, etc.).

#### 1. Frontend: Registering a Command (TypeScript)

This code goes in your frontend plugin file (e.g., `src/plugin.ts`). It adds a "Call My Backend" command to the command palette.

```typescript
import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import { ICommandPalette, showDialog } from '@jupyterlab/apputils';
import { ServerConnection } from '@jupyterlab/services';

// Define a unique ID for your command
const COMMAND_ID = 'my-extension:call-backend';

const plugin: JupyterFrontEndPlugin<void> = {
  id: 'my-extension:plugin',
  autoStart: true,
  requires: [ICommandPalette],
  activate: (app: JupyterFrontEnd, palette: ICommandPalette) => {
    console.log('My frontend extension is activated!');

    // Add the command to the application's command registry
    app.commands.addCommand(COMMAND_ID, {
      label: 'Call My Backend',
      execute: async () => {
        // --- This is where the action happens ---
        try {
          // 1. Make a request to the backend API endpoint
          const response = await ServerConnection.makeRequest(
            `${ServerConnection.makeSettings().baseUrl}my-extension/hello`,
            { method: 'GET' },
            ServerConnection.makeSettings()
          );

          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }

          const data = await response.json();

          // 2. Show the response in a dialog box
          showDialog({
            title: 'Backend Response',
            body: `The backend says: "${data.message}"`,
            buttons: [showDialog.okButton({ label: 'OK' })]
          });
        } catch (error) {
          console.error('Error calling backend:', error);
          showDialog({
            title: 'Error',
            body: `Failed to call backend: ${error}`,
            buttons: [showDialog.okButton({ label: 'OK' })]
          });
        }
      }
    });

    // Add the command to the command palette for easy access
    palette.addItem({
      command: COMMAND_ID,
      category: 'My Extension'
    });
  }
};

export default plugin;
```

#### 2. Backend: Creating an API Handler (Python)

This code goes in your server extension's Python package (e.g., in a file named `handlers.py`). It creates the `/my-extension/hello` API endpoint that the frontend calls.

```python
import json
from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
import tornado

class HelloWorldHandler(APIHandler):
    # The following decorator should be present on all verb methods (head, get, post, etc.)
    # to ensure that the user is authenticated.
    @tornado.web.authenticated
    def get(self):
        # --- This is where the action happens ---
        self.finish(json.dumps({
            "message": "Hello from the Python backend!"
        }))

def setup_handlers(web_app):
    host_pattern = ".*$"
    base_url = web_app.settings["base_url"]

    # The API route is created by joining the base URL with your custom endpoint
    route_pattern = url_path_join(base_url, "my-extension", "hello")

    # Add the handler to the web application
    handlers = [(route_pattern, HelloWorldHandler)]
    web_app.add_handlers(host_pattern, handlers)

# This function is called when the server extension is loaded.
# It's usually in your package's __init__.py file.
def _load_jupyter_server_extension(server_app):
    """Registers the API handler to receive HTTP requests."""
    setup_handlers(server_app.web_app)
    server_app.log.info("My server extension is loaded!")

```

### Semantic Scholar API Clientation. (2024). _Semantic Scholar_. Retrieved from <https://www.semanticscholar.org/product/api>

[4] PyMuPDF Documentation. (2024). _PyMuPDF_. Retrieved from <https://pymupdf.readthedocs.io/en/latest/>

[5] Statsmodels Documentation. (2024). _Statsmodels_. Retrieved from <https://www.statsmodels.org/stable/index.html>

[6] What Works Clearinghouse. (2022). _WWC Standards Handbook, Version 5.0_. U.S. Department of Education, Institute of Education Sciences. Retrieved from <https://ies.ed.gov/ncee/wwc/Docs/referenceresources/Final_WWC-HandbookVer5.0-0-508.pdf>

---

## Appendix H: JupyterLab Architecture Notes

This appendix provides a high-level overview of the JupyterLab architecture, focusing on the monorepo structure and the role of Lumino.

### Monorepo Structure

JupyterLab is a **monorepo** containing:

- Many TypeScript packages (in `packages/`)
- One Python package (in `jupyterlab/`)

The Python package distributes the bundled-and-compiled TypeScript code.

### Key Directories

#### `packages/` - NPM Packages

- Contains many TypeScript sub-packages
- Independently versioned and published to npmjs.org
- Compiled to JavaScript and bundled with Python package
- **Common pattern**: Component package + `-extension` package
  - Example: `@jupyterlab/notebook` (component) + `@jupyterlab/notebook-extension` (integration)

#### `jupyterlab/` - Python Package

- Server-side code
- Command line interface
- Entry points
- Python tests
- Final built JavaScript assets

### Lumino

**What it is**: A set of JavaScript packages (written in TypeScript) that provide a rich toolkit of widgets, layouts, events, and data structures.

**Purpose**: Enable developers to construct extensible, high-performance, desktop-like web applications.

**History**: Formerly known as PhosphorJS.

**Key Components**:

- Widgets (UI components)
- Layouts (DockPanel, SplitPanel, TabPanel, etc.)
- Events system
- Data structures (like DataGrid)

**Why JupyterLab uses it**: JupyterLab is built on top of Lumino to provide its desktop-like interface with dockable panels, tabs, and complex layouts.
