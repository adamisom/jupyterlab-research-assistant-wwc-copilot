# Parallelization Plan for Stage 1 Implementation

**Goal**: Enable 2-3 developers to work simultaneously on Stage 1 with minimal conflicts.

**Strategy**: Split work by layer (backend vs frontend) and by feature independence.

---

## Worktree Setup

Each developer should create a separate worktree to avoid conflicts:

```bash
# From the main repository directory
cd /Users/adamisom/Desktop/jupyterlab-research-assistant-wwc-copilot

# Create worktrees for each developer
git worktree add ../jupyterlab-research-assistant-wwc-copilot-backend backend-work
git worktree add ../jupyterlab-research-assistant-wwc-copilot-frontend frontend-work
git worktree add ../jupyterlab-research-assistant-wwc-copilot-integration integration-work

# Each developer works in their own directory
# Backend dev: cd ../jupyterlab-research-assistant-wwc-copilot-backend
# Frontend dev: cd ../jupyterlab-research-assistant-wwc-copilot-frontend
# Integration dev: cd ../jupyterlab-research-assistant-wwc-copilot-integration
```

**Important**: All worktrees share the same Git history but have separate working directories. Each developer can commit independently.

---

## Option 1: Two-Person Split (Recommended)

### Person A: Backend Developer
**Focus**: All server-side implementation

**Tasks** (in order):
1. **Database Setup** (`jupyterlab_research_assistant_wwc_copilot/database/`)
   - Create `models.py` with Paper, StudyMetadata, LearningScienceMetadata
   - Create `db_manager.py` with DatabaseManager class
   - Test database creation and basic CRUD operations
   - **Deliverable**: Working database with test data

2. **PDF Parser Service** (`jupyterlab_research_assistant_wwc_copilot/services/pdf_parser.py`)
   - Implement PDFParser class with PyMuPDF
   - Handle error cases (corrupted PDFs, large files)
   - **Deliverable**: Can extract text from sample PDFs

3. **Semantic Scholar API Client** (`jupyterlab_research_assistant_wwc_copilot/services/semantic_scholar.py`)
   - Implement SemanticScholarAPI class
   - Add rate limiting
   - **Deliverable**: Can search Semantic Scholar and get paper details

4. **API Routes** (`jupyterlab_research_assistant_wwc_copilot/routes.py`)
   - Implement LibraryHandler (GET, POST)
   - Implement SearchHandler (GET)
   - Implement DiscoveryHandler (GET)
   - Implement ImportHandler (POST)
   - **Deliverable**: All endpoints working, testable with curl

**Dependencies**: None (can work completely independently)

**Testing**: Use curl or Postman to test endpoints

**Branch**: `backend-work` (worktree)

---

### Person B: Frontend Developer
**Focus**: All client-side implementation

**Tasks** (in order):
1. **API Client** (`src/api.ts`)
   - Define TypeScript interfaces (Paper, APIResponse, etc.)
   - Implement API functions (getLibrary, searchLibrary, searchSemanticScholar, importPaper, importPDF)
   - **Note**: Can mock backend responses initially using `requestAPI` with test data
   - **Deliverable**: API client functions with proper types

2. **PaperCard Component** (`src/widgets/PaperCard.tsx`)
   - Simple component to display paper information
   - **Deliverable**: Renders paper data nicely

3. **DiscoveryTab Component** (`src/widgets/DiscoveryTab.tsx`)
   - Search UI for Semantic Scholar
   - Results list with PaperCard components
   - Import button functionality
   - **Deliverable**: Can search (mocked) and display results

4. **LibraryTab Component** (`src/widgets/LibraryTab.tsx`)
   - Display papers from local library
   - Search functionality
   - **Deliverable**: Can display and search library papers

5. **ResearchLibraryPanel Component** (`src/widgets/ResearchLibraryPanel.tsx`)
   - Main panel with tab switching
   - Integrates DiscoveryTab and LibraryTab
   - **Deliverable**: Complete sidebar panel with tabs

6. **Plugin Registration** (`src/index.ts`)
   - Register panel with JupyterLab
   - Add to command palette
   - **Deliverable**: Panel appears in JupyterLab sidebar

**Dependencies**: Can work independently by mocking backend API responses

**Testing**: Use mock data in `requestAPI` or create a simple mock server

**Branch**: `frontend-work` (worktree)

---

## Option 2: Three-Person Split

### Person A: Backend Core
**Focus**: Database and core services

**Tasks**:
1. Database models and manager
2. PDF parser service
3. Basic API routes (LibraryHandler, SearchHandler)

**Deliverable**: Core backend functionality working

---

### Person B: Backend External APIs
**Focus**: External service integration

**Tasks**:
1. Semantic Scholar API client
2. DiscoveryHandler route
3. ImportHandler route (PDF upload)

**Deliverable**: External API integration complete

**Note**: Can start after Person A completes database setup

---

### Person C: Frontend
**Focus**: All frontend work (same as Person B in Option 1)

**Tasks**: Same as Person B in Option 1

**Deliverable**: Complete frontend implementation

---

## Coordination Points

### API Contract Agreement (Before Starting)
**Critical**: Both backend and frontend developers must agree on API contract:

```typescript
// Shared API contract (create docs/api-contract.md)

// GET /jupyterlab-research-assistant-wwc-copilot/library
Response: {
  status: "success" | "error",
  data: Paper[],
  message?: string
}

// GET /jupyterlab-research-assistant-wwc-copilot/search?q=query
Response: {
  status: "success" | "error",
  data: Paper[],
  message?: string
}

// GET /jupyterlab-research-assistant-wwc-copilot/discovery?q=query&year=2020-2024
Response: {
  status: "success" | "error",
  data: {
    data: Paper[],
    total: number
  },
  message?: string
}

// POST /jupyterlab-research-assistant-wwc-copilot/library
Request Body: Paper (JSON)
Response: {
  status: "success" | "error",
  data: Paper,
  message?: string
}

// POST /jupyterlab-research-assistant-wwc-copilot/import
Request: FormData with 'file' field
Response: {
  status: "success" | "error",
  data: Paper,
  message?: string
}

// Paper interface
interface Paper {
  id?: number;
  paperId?: string;
  title: string;
  authors: string[];
  year?: number;
  doi?: string;
  s2_id?: string;
  citation_count?: number;
  abstract?: string;
  full_text?: string;
  study_metadata?: {...};
  learning_science_metadata?: {...};
}
```

**Action**: Create `docs/api-contract.md` with this contract before starting.

---

### Daily Sync Points

1. **Morning Standup** (15 min):
   - What did you complete yesterday?
   - What are you working on today?
   - Any blockers?

2. **API Contract Changes**:
   - If backend needs to change API, notify frontend immediately
   - Update `docs/api-contract.md` immediately
   - Frontend can adapt or wait

3. **Integration Checkpoints**:
   - End of Day 1: Backend has at least one endpoint working
   - End of Day 2: Frontend can connect to real backend
   - End of Day 3: Full integration test

---

## Workflow

### Initial Setup (All Developers)
```bash
# Each developer in their worktree
cd ../jupyterlab-research-assistant-wwc-copilot-backend  # or -frontend, -integration

# Activate environment
conda activate <env>  # or source venv/bin/activate

# Install dependencies
pip install -e ".[dev,test]"
jlpm install

# Link extension (backend dev only needs this once)
jupyter labextension develop . --overwrite
jupyter server extension enable jupyterlab_research_assistant_wwc_copilot
```

### Daily Workflow

**Backend Developer**:
```bash
# Make changes to Python files
# Test with curl or Postman
# Commit to backend-work branch
git add .
git commit -m "feat(backend): implement LibraryHandler"
git push origin backend-work
```

**Frontend Developer**:
```bash
# Make changes to TypeScript files
# Run watch mode
jlpm watch  # In one terminal
jupyter lab  # In another terminal
# Test in browser
# Commit to frontend-work branch
git add .
git commit -m "feat(frontend): implement DiscoveryTab component"
git push origin frontend-work
```

### Integration Workflow

**Integration Developer** (or Person A/B together):
```bash
# Merge both branches
git checkout main
git merge backend-work
git merge frontend-work
# Resolve conflicts if any
# Test full integration
# Fix any integration issues
git commit -m "feat: integrate backend and frontend"
```

---

## Conflict Prevention

### File Ownership
- **Backend dev**: All files in `jupyterlab_research_assistant_wwc_copilot/` (Python)
- **Frontend dev**: All files in `src/` (TypeScript)
- **Shared files**: 
  - `package.json` (frontend dev owns, backend dev may need to add Python deps)
  - `pyproject.toml` (backend dev owns, frontend dev may need to add JS deps)
  - `docs/` (coordinate on updates)

### Dependency Management
- **Backend adds Python dependency**: Update `pyproject.toml`, notify team
- **Frontend adds NPM dependency**: Update `package.json`, run `jlpm install`, notify team
- **Both need to run**: `pip install -e .` after dependency changes

### Testing Strategy
- **Backend**: Test independently with curl/Postman
- **Frontend**: Test with mocked API responses initially
- **Integration**: Test with real backend once both are ready

---

## Recommended Timeline (2-Person Split)

### Day 1
- **Morning**: Setup worktrees, agree on API contract
- **Backend**: Database models + db_manager (4-6 hours)
- **Frontend**: API client types + PaperCard component (4-6 hours)
- **Evening**: Sync, backend shares working endpoint, frontend tests with real API

### Day 2
- **Backend**: PDF parser + Semantic Scholar API client (4-6 hours)
- **Frontend**: DiscoveryTab component (4-6 hours)
- **Evening**: Sync, test DiscoveryTab with real Semantic Scholar endpoint

### Day 3
- **Backend**: All API routes complete (4-6 hours)
- **Frontend**: LibraryTab + ResearchLibraryPanel + plugin registration (4-6 hours)
- **Evening**: Full integration test, fix any issues

### Day 4
- **Both**: Polish, error handling, edge cases
- **Integration**: End-to-end testing, documentation

---

## Recommended Timeline (3-Person Split)

### Day 1
- **Backend Core**: Database models + db_manager (4-6 hours)
- **Backend External**: Wait or help with database
- **Frontend**: API client types + PaperCard (4-6 hours)

### Day 2
- **Backend Core**: PDF parser + basic routes (4-6 hours)
- **Backend External**: Semantic Scholar API client (4-6 hours)
- **Frontend**: DiscoveryTab component (4-6 hours)

### Day 3
- **Backend Core**: Complete all routes (2-3 hours)
- **Backend External**: ImportHandler + integration (2-3 hours)
- **Frontend**: LibraryTab + Panel + plugin (4-6 hours)

### Day 4
- **All**: Integration, testing, polish

---

## Merge Strategy

### Option A: Feature Branches (Recommended)
- Each worktree works on separate branch
- Merge to main when feature complete
- Use pull requests for review

### Option B: Direct Commits
- Each worktree commits directly to main
- Coordinate on shared files
- Faster but riskier

**Recommendation**: Use Option A with feature branches.

---

## Troubleshooting

### Issue: Worktree conflicts
**Solution**: Each worktree is independent, conflicts only happen when merging branches

### Issue: Shared dependency conflicts
**Solution**: Coordinate on `package.json` and `pyproject.toml` changes

### Issue: API contract drift
**Solution**: Always update `docs/api-contract.md` immediately, frontend adapts

### Issue: Testing without backend
**Solution**: Frontend can mock API responses in `src/api.ts`:
```typescript
// Temporary mock for development
export async function getLibrary(): Promise<Paper[]> {
  // TODO: Remove mock when backend is ready
  if (process.env.NODE_ENV === 'development') {
    return [
      { id: 1, title: "Mock Paper", authors: ["Author 1"], year: 2023 }
    ];
  }
  // Real implementation
  const response = await requestAPI<APIResponse<Paper[]>>('library', {
    method: 'GET'
  });
  // ...
}
```

---

## Success Criteria

- ✅ Backend: All endpoints working, testable with curl
- ✅ Frontend: All components render, can interact with UI
- ✅ Integration: Full workflow works (search → import → view in library)
- ✅ No merge conflicts in shared files
- ✅ API contract matches between backend and frontend

---

## Next Steps

1. **Choose split**: 2-person or 3-person?
2. **Create worktrees**: Run setup commands above
3. **Agree on API contract**: Create `docs/api-contract.md`
4. **Start work**: Each developer follows their task list
5. **Daily sync**: 15-min standup each day
6. **Merge when ready**: Integrate branches, test, deploy

