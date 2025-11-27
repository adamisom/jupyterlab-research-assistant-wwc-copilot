# Demo Script: JupyterLab Research Assistant & WWC Co-Pilot

**Purpose**: Quick demonstration of extension features in a Binder JupyterLab environment  
**Duration**: ~10-15 minutes  
**Audience**: Researchers, educators, or developers interested in research management tools

---

## JupyterLab Architecture & Ecosystem (Brief Overview)

**What is JupyterLab?**
JupyterLab is a web-based interactive development environment built on a modular, extensible architecture. Think of it like VS Code or RStudio, but running in your browser and designed specifically for data science, research, and computational work.

**Key Architectural Concepts:**

1. **Frontend + Backend Split**:
   - **Frontend**: TypeScript/React application running in your browser
   - **Backend**: Python server (Jupyter Server) that handles file operations, kernels, and custom APIs
   - Communication happens via REST APIs

2. **Extension System**:
   - Everything in JupyterLab is an **extension** (even core features like notebooks and file browser)
   - Extensions can add:
     - **Sidebar panels** (like our Research Library)
     - **Main area widgets** (like our Synthesis Workbench)
     - **Commands** (accessible via command palette)
     - **Backend APIs** (for custom server functionality)

3. **Plugin Architecture**:
   - Extensions use a **plugin system** with dependency injection
   - Services are provided via **Tokens** (unique identifiers)
   - Plugins can consume and provide services to each other

4. **Lumino Widgets**:
   - The UI foundation is built on **Lumino** (formerly Phosphor)
   - Provides drag-and-drop, layouts, and messaging between widgets
   - React components are wrapped in Lumino widgets for integration

**Why This Matters for Our Extension:**
- Our extension follows the same patterns as core JupyterLab features
- It integrates seamlessly: appears in sidebar, uses JupyterLab's theming, respects user settings
- Backend runs as a **Jupyter Server extension** (Python), frontend as a **JupyterLab extension** (TypeScript)
- Data is stored locally (SQLite database) in the user's JupyterLab data directory
- All communication between frontend and backend uses JupyterLab's standard API patterns

**In Practice:**
When you use our extension, you're experiencing JupyterLab's extensibility in action. The Research Library panel in the sidebar, the Synthesis Workbench in the main area, and the backend API endpoints all follow JupyterLab's established patterns, making it feel like a native part of the environment.

---

## Pre-Demo Setup

1. **Open Binder JupyterLab** (extension should already be installed)
2. **Verify extension is loaded**:
   - Check left sidebar for "Research Library" panel
   - If not visible: `View` → `Show Left Sidebar` or look for the extension icon

---

## Demo Flow

### 1. Opening the Extension (30 seconds)

**What to show:**
- Left sidebar panel: "Research Library"
- Two tabs: "Library" and "Discovery"

**What to say:**
> "This extension provides a Research Library for managing academic papers and a Discovery engine for finding new research. Let me show you both."

---

### 2. Discovery Engine - Finding Papers (2-3 minutes)

**Steps:**
1. Click on **"Discovery"** tab
2. Search for: `"spaced repetition learning"`
3. Show results with:
   - Paper titles
   - Authors and year
   - Citation counts
   - **Open Access PDF** badges (if available)
4. Click on a paper with "Open Access PDF" badge
   - Show it opens in a new tab
5. Click **"View Details"** on another paper
   - Show detailed view with abstract, metadata
6. Click **"Import to Library"** on 2-3 papers

**What to say:**
> "The Discovery tab searches Semantic Scholar and OpenAlex. You can see open access PDFs are highlighted, and you can import papers directly to your library with one click."

---

### 3. Library - Managing Papers (2-3 minutes)

**Steps:**
1. Switch to **"Library"** tab
2. Show imported papers:
   - Authors and Year displayed (or "could not detect" if extraction failed)
   - "Full Local PDF" badge for uploaded PDFs
   - "Open Access PDF" link for external PDFs
   - "Metadata Only" badge for papers without PDFs
3. Click **"View Details"** on a paper
   - Show full abstract
   - Show all metadata
   - If it has a PDF, show "Open PDF" button
4. Click **"Open PDF"** (if available)
   - Show PDF opens in new tab via blob URL

**What to say:**
> "The Library shows all your papers. For uploaded PDFs, we extract authors, year, and abstracts automatically. You can view PDFs directly in the browser."

---

### 4. Uploading a PDF (2 minutes)

**Steps:**
1. In Library tab, look for upload option (or use file browser)
2. Upload a PDF file
3. Show it appears in Library
4. Show extracted metadata:
   - Authors (or "could not detect")
   - Year (or "could not detect")
   - Abstract (first paragraph from first page)
5. Click "View Details" to show full abstract
6. Click "Open PDF" to show PDF viewing

**What to say:**
> "When you upload a PDF, we automatically extract metadata from the first page. The abstract extraction stops at 'Keywords:' and tries to remove author information."

---

### 5. Synthesis Engine - Meta-Analysis (3-4 minutes)

**Steps:**
1. Select 3+ papers in Library (checkboxes)
2. Click **"Open WWC Co-Pilot"** button
3. Show Synthesis Workbench opens in main area
4. Navigate to **"Meta-Analysis"** tab
5. Show:
   - Papers listed with effect sizes
   - Forest plot visualization
   - Summary statistics (overall effect, heterogeneity)
6. If papers have subgroups, show **"Subgroup Analysis"** tab
7. Show **"Publication Bias"** tab:
   - Egger's test results
   - Funnel plot

**What to say:**
> "The Synthesis Engine lets you perform meta-analyses on selected papers. It automatically calculates effect sizes, creates forest plots, and assesses publication bias using Egger's test."

---

### 6. WWC Quality Assessment (2-3 minutes)

**Steps:**
1. In Synthesis Workbench, go to **"WWC Co-Pilot"** tab
2. Select a single paper
3. Walk through WWC assessment:
   - Show the multi-step wizard interface
   - Show questions about study design, sample size, etc.
   - Show how it guides through WWC Handbook v5.0 criteria
4. Show final assessment result:
   - Meets WWC Standards / Does Not Meet / Meets with Reservations

**What to say:**
> "The WWC Co-Pilot guides you through the What Works Clearinghouse quality assessment process. It follows the WWC Handbook v5.0 standards and helps ensure consistent, rigorous evaluations."

---

### 7. Conflict Detection (1-2 minutes)

**Steps:**
1. In Synthesis Workbench, go to **"Conflict Detection"** tab
2. Show:
   - Papers being compared
   - AI-extracted findings preview
   - Conflict detection results
   - Highlighted conflicting findings

**What to say:**
> "Conflict Detection uses natural language inference to identify when findings from different studies contradict each other. This helps you understand where research consensus breaks down."

---

### 8. Export Features (1 minute)

**Steps:**
1. In Library, show export options (if available)
2. Or in Synthesis Workbench, show export options
3. Mention supported formats:
   - JSON
   - CSV
   - BibTeX
   - Markdown

**What to say:**
> "You can export your library or synthesis results in multiple formats for use in other tools or for sharing with collaborators."

---

## Key Talking Points

### Strengths to Emphasize:
1. **Integrated workflow**: Discovery → Library → Synthesis all in one place
2. **Automatic metadata extraction**: Authors, year, abstracts from PDFs
3. **Open access support**: Easy access to open access PDFs
4. **WWC standards compliance**: Built-in quality assessment
5. **Meta-analysis tools**: Forest plots, subgroup analysis, publication bias
6. **Conflict detection**: AI-powered finding comparison

### Technical Highlights:
- Built on JupyterLab (familiar environment for researchers)
- Python backend + TypeScript frontend
- SQLite database for local storage
- Integrates with Semantic Scholar and OpenAlex APIs
- Uses statsmodels for meta-analysis
- NLI models for conflict detection

---

## Troubleshooting Tips

**If extension doesn't appear:**
- Check browser console for errors
- Verify extension is enabled: `jupyter labextension list`
- Try refreshing the page

**If PDFs don't open:**
- Check browser popup blocker settings
- Verify PDF file is valid
- Check browser console for errors

**If discovery doesn't work:**
- Check internet connection
- Semantic Scholar/OpenAlex APIs may be rate-limited
- Try a different search query

---

## Demo Checklist

- [ ] Extension opens in sidebar
- [ ] Discovery search works
- [ ] Open Access PDF links work
- [ ] Papers can be imported to Library
- [ ] Library displays papers with metadata
- [ ] PDF upload and extraction works
- [ ] PDF viewing works (blob URLs)
- [ ] Synthesis Workbench opens
- [ ] Meta-analysis runs and shows results
- [ ] WWC assessment wizard works
- [ ] Conflict detection shows results

---

## Quick Demo (5-minute version)

If short on time, focus on:
1. **Discovery** → Search → Import papers (1 min)
2. **Library** → Show papers → View details → Open PDF (2 min)
3. **Synthesis** → Select papers → Show meta-analysis results (2 min)

---

## Post-Demo Q&A Topics

- Installation and setup
- Database location and backup
- API rate limits
- Extending functionality
- Integration with other tools
- Performance with large libraries

---

**Note**: This is a temporary demo script. Update as features evolve or remove after creating a permanent version.

