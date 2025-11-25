# Stage 2 Parallelization Guide for Two Agents

**Purpose**: Split Stage 2 implementation work between two agents working simultaneously in the same repository.

---

## Setup Instructions

### Both Agents (Same Repository)
```bash
# Both agents work in the same repository on the same branch
cd /path/to/jupyterlab-research-assistant-wwc-copilot
# Set up environment, install dependencies, etc.
```

**Note**: Agent 1 (Backend) and Agent 2 (Frontend) touch completely different files with zero overlap, so they can work simultaneously in the same repository without conflicts.

---

## Parallelization Strategy Options

### Option 1: Backend/Frontend Split (Recommended)

**Rationale**: Clean separation by layer. Backend and frontend rarely touch the same files.

#### Agent 1: Backend Implementation
**Focus**: All backend services and API routes

**Phases**:
- ✅ Phase 2.1: WWC Assessment Engine (`services/wwc_assessor.py`)
- ✅ Phase 2.2: Meta-Analysis Engine (`services/meta_analyzer.py`)
- ✅ Phase 2.3: Forest Plot Generator (`services/visualizer.py`)
- ✅ Phase 2.4: Conflict Detection (`services/conflict_detector.py`) - Optional
- ✅ Phase 2.5: API Routes (`routes.py` - add WWC routes)

**Files to Create/Modify**:
- `jupyterlab_research_assistant_wwc_copilot/services/wwc_assessor.py` (NEW)
- `jupyterlab_research_assistant_wwc_copilot/services/meta_analyzer.py` (NEW)
- `jupyterlab_research_assistant_wwc_copilot/services/visualizer.py` (NEW)
- `jupyterlab_research_assistant_wwc_copilot/services/conflict_detector.py` (NEW)
- `jupyterlab_research_assistant_wwc_copilot/routes.py` (MODIFY - add handlers)
- `jupyterlab_research_assistant_wwc_copilot/tests/test_wwc_assessor.py` (NEW)
- `jupyterlab_research_assistant_wwc_copilot/tests/test_meta_analyzer.py` (NEW)
- `jupyterlab_research_assistant_wwc_copilot/tests/test_conflict_detector.py` (NEW)
- `pyproject.toml` (MODIFY - add dependencies: statsmodels, matplotlib, numpy)

**Potential Conflicts**: 
- **NONE** - Agent 2 (Frontend) does not touch any backend files

**Testing**: Use curl/Postman to test API endpoints

---

#### Agent 2: Frontend Implementation
**Focus**: All frontend components and API client

**Phases**:
- ✅ Phase 2.6: Update API Client (`api.ts`)
- ✅ Phase 2.7: Update Library Tab for Multi-Select (`LibraryTab.tsx`, `PaperCard.tsx`)
- ✅ Phase 2.8: WWC Co-Pilot Widget (`WWCCoPilot.tsx`)
- ✅ Phase 2.9: Synthesis Workbench Widget (`SynthesisWorkbench.tsx`)
- ✅ Phase 2.10: Meta-Analysis View Component (`MetaAnalysisView.tsx`)
- ✅ Phase 2.11: Conflict View Component (`ConflictView.tsx`)
- ✅ Phase 2.12: Integrate into Main Plugin (`index.ts`)

**Files to Create/Modify**:
- `src/api.ts` (MODIFY - add WWC API functions and types)
- `src/widgets/LibraryTab.tsx` (MODIFY - add multi-select)
- `src/widgets/PaperCard.tsx` (MODIFY - add checkbox)
- `src/widgets/WWCCoPilot.tsx` (NEW)
- `src/widgets/SynthesisWorkbench.tsx` (NEW)
- `src/widgets/MetaAnalysisView.tsx` (NEW)
- `src/widgets/ConflictView.tsx` (NEW)
- `src/index.ts` (MODIFY - add commands and widget registration)

**Potential Conflicts**:
- **NONE** - Agent 1 (Backend) does not touch any frontend files

**Testing**: Test in browser with JupyterLab running

---

### Option 2: Feature-Based Split (WWC vs Synthesis)

**Rationale**: Complete feature ownership per agent.

#### Agent 1: WWC Co-Pilot Feature
**Focus**: WWC assessment end-to-end (backend + frontend)

**Phases**:
- ✅ Phase 2.1: WWC Assessment Engine (`services/wwc_assessor.py`)
- ✅ Phase 2.5: WWC API Route (`routes.py` - WWCAssessmentHandler only)
- ✅ Phase 2.6: WWC API Client Functions (`api.ts` - WWC functions only)
- ✅ Phase 2.8: WWC Co-Pilot Widget (`WWCCoPilot.tsx`)
- ✅ Phase 2.12: WWC Command Integration (`index.ts` - WWC command only)

**Files**:
- Backend: `wwc_assessor.py`, `routes.py` (partial), `test_wwc_assessor.py`
- Frontend: `api.ts` (partial), `WWCCoPilot.tsx`, `index.ts` (partial)

**Potential Conflicts**:
- `routes.py` - Both modify (need coordination on handler registration)
- `api.ts` - Both add functions (easy to merge)
- `index.ts` - Both add commands (easy to merge)

---

#### Agent 2: Synthesis Engine Feature
**Focus**: Meta-analysis and conflict detection end-to-end (backend + frontend)

**Phases**:
- ✅ Phase 2.2: Meta-Analysis Engine (`services/meta_analyzer.py`)
- ✅ Phase 2.3: Forest Plot Generator (`services/visualizer.py`)
- ✅ Phase 2.4: Conflict Detection (`services/conflict_detector.py`)
- ✅ Phase 2.5: Synthesis API Routes (`routes.py` - MetaAnalysisHandler, ConflictDetectionHandler)
- ✅ Phase 2.6: Synthesis API Client Functions (`api.ts` - meta-analysis and conflict functions)
- ✅ Phase 2.7: Multi-Select in Library Tab (`LibraryTab.tsx`, `PaperCard.tsx`)
- ✅ Phase 2.9: Synthesis Workbench Widget (`SynthesisWorkbench.tsx`)
- ✅ Phase 2.10: Meta-Analysis View Component (`MetaAnalysisView.tsx`)
- ✅ Phase 2.11: Conflict View Component (`ConflictView.tsx`)
- ✅ Phase 2.12: Synthesis Command Integration (`index.ts` - synthesis command)

**Files**:
- Backend: `meta_analyzer.py`, `visualizer.py`, `conflict_detector.py`, `routes.py` (partial), tests
- Frontend: `api.ts` (partial), `LibraryTab.tsx`, `PaperCard.tsx`, `SynthesisWorkbench.tsx`, `MetaAnalysisView.tsx`, `ConflictView.tsx`, `index.ts` (partial)

**Potential Conflicts**:
- `routes.py` - Both modify (need coordination)
- `api.ts` - Both add functions (easy to merge)
- `index.ts` - Both add commands (easy to merge)
- `LibraryTab.tsx` / `PaperCard.tsx` - Agent 2 modifies, Agent 1 doesn't touch (no conflict)

---

### Option 3: Service/UI Split (Hybrid)

**Rationale**: Agent 1 implements all services, Agent 2 implements all UI that consumes them.

#### Agent 1: All Backend Services + API Routes
**Focus**: Complete backend implementation

**Phases**:
- ✅ Phase 2.1: WWC Assessment Engine
- ✅ Phase 2.2: Meta-Analysis Engine
- ✅ Phase 2.3: Forest Plot Generator
- ✅ Phase 2.4: Conflict Detection
- ✅ Phase 2.5: All API Routes (WWC, Meta-Analysis, Conflict)

**Files**: All backend service files + routes.py + tests

---

#### Agent 2: All Frontend Components
**Focus**: Complete frontend implementation

**Phases**:
- ✅ Phase 2.6: Update API Client (all functions)
- ✅ Phase 2.7: Multi-Select in Library Tab
- ✅ Phase 2.8: WWC Co-Pilot Widget
- ✅ Phase 2.9: Synthesis Workbench Widget
- ✅ Phase 2.10: Meta-Analysis View Component
- ✅ Phase 2.11: Conflict View Component
- ✅ Phase 2.12: Plugin Integration

**Files**: All frontend widget files + api.ts + index.ts

---

## Recommended Approach: Option 1 (Backend/Frontend Split)

**Why Option 1 is Best**:
1. **Zero File Conflicts**: Backend and frontend touch completely different files
2. **Clear Boundaries**: Easy to define what each agent owns
3. **Independent Testing**: Agent 1 can test with curl, Agent 2 can mock API responses
4. **Natural Workflow**: Backend-first, then frontend consumes it
5. **No Worktree Needed**: Can work simultaneously in same repository

**File Overlap Analysis**:
- **Agent 1 (Backend) touches**: `routes.py`, `pyproject.toml`, new service files, test files
- **Agent 2 (Frontend) touches**: `src/api.ts`, `src/index.ts`, widget files
- **Shared files**: **ZERO** - completely separate file sets

**Coordination Points**:
- **API Contract**: Agent 1 should commit backend API endpoints first so Agent 2 knows response formats
- **Type Definitions**: Agent 2 defines TypeScript interfaces based on Agent 1's API responses (can check Agent 1's commits)

**Workflow**:
1. Both agents work simultaneously in the same repository
2. Agent 1 commits backend services and API routes as they're completed
3. Agent 2 pulls Agent 1's commits regularly to see API contract
4. Agent 2 commits frontend components independently
5. No merge conflicts expected since files don't overlap

---

## Detailed Work Breakdown (Option 1)

### Agent 1: Backend (Estimated: 8-12 hours)

#### Phase 2.1: WWC Assessment Engine (2-3 hours)
- Create `services/wwc_assessor.py`
- Implement `WWCQualityAssessor` class
- Implement `WWCAssessment` dataclass
- Add unit tests
- **Manual Test**: Run test cases from guide

#### Phase 2.2: Meta-Analysis Engine (2-3 hours)
- Create `services/meta_analyzer.py`
- Implement `MetaAnalyzer` class
- Add unit tests
- **Manual Test**: Test with sample studies

#### Phase 2.3: Forest Plot Generator (1-2 hours)
- Create `services/visualizer.py`
- Implement `Visualizer.create_forest_plot()`
- **Manual Test**: Generate plot, save to file, verify image

#### Phase 2.4: Conflict Detection (2-3 hours, Optional)
- Create `services/conflict_detector.py`
- Implement `ConflictDetector` class
- Handle optional transformers dependency
- **Manual Test**: Test with sample findings

#### Phase 2.5: API Routes (1-2 hours)
- Update `routes.py`:
  - Add imports for new services
  - Add `WWCAssessmentHandler`
  - Add `MetaAnalysisHandler`
  - Add `ConflictDetectionHandler`
  - Update `setup_route_handlers()`
- Update `pyproject.toml` with dependencies
- **Manual Test**: Test all endpoints with curl

**Deliverable**: Fully functional backend API endpoints

---

### Agent 2: Frontend (Estimated: 10-14 hours)

#### Phase 2.6: Update API Client (1-2 hours)
- Update `src/api.ts`:
  - Add TypeScript interfaces (IWWCAssessment, IMetaAnalysisResult, etc.)
  - Add `runWWCAssessment()` function
  - Add `performMetaAnalysis()` function
  - Add `detectConflicts()` function
- **Manual Test**: Verify types compile, functions are exported

#### Phase 2.7: Multi-Select in Library Tab (1-2 hours)
- Update `src/widgets/LibraryTab.tsx`:
  - Add selectedPapers state
  - Add toggle selection handler
  - Add "Synthesize Studies" button
- Update `src/widgets/PaperCard.tsx`:
  - Add checkbox prop and rendering
- **Manual Test**: Select papers, verify button appears

#### Phase 2.8: WWC Co-Pilot Widget (2-3 hours)
- Create `src/widgets/WWCCoPilot.tsx`
- Implement judgment form
- Implement assessment display
- Add styling
- **Manual Test**: Open widget, change judgments, verify assessment updates

#### Phase 2.9: Synthesis Workbench Widget (2-3 hours)
- Create `src/widgets/SynthesisWorkbench.tsx`
- Implement tab system
- Add action buttons
- Integrate MetaAnalysisView and ConflictView
- **Manual Test**: Open workbench, run analyses

#### Phase 2.10: Meta-Analysis View Component (1-2 hours)
- Create `src/widgets/MetaAnalysisView.tsx`
- Display summary statistics
- Display forest plot image
- Display study table
- **Manual Test**: Verify all data displays correctly

#### Phase 2.11: Conflict View Component (1 hour)
- Create `src/widgets/ConflictView.tsx`
- Display contradictions list
- Format conflict items
- **Manual Test**: Verify conflicts display correctly

#### Phase 2.12: Plugin Integration (1-2 hours)
- Update `src/index.ts`:
  - Add synthesis workbench command
  - Add WWC co-pilot command
  - Wire up LibraryTab button to command
- **Manual Test**: Test commands from palette, verify widgets open

**Deliverable**: Fully functional frontend UI

---

## Conflict Resolution Guide

### File Overlap: ZERO

**Agent 1 (Backend) modifies**:
- `jupyterlab_research_assistant_wwc_copilot/routes.py`
- `jupyterlab_research_assistant_wwc_copilot/services/*.py` (new files)
- `jupyterlab_research_assistant_wwc_copilot/tests/*.py` (new files)
- `pyproject.toml`

**Agent 2 (Frontend) modifies**:
- `src/api.ts`
- `src/index.ts`
- `src/widgets/*.tsx` (new and modified files)

**Conclusion**: **Zero file overlap** - no conflicts possible. Both agents can work simultaneously without coordination on file access.

---

## Simple Workflow (No Special Coordination Needed)

### Before Starting
1. Both agents confirm they're using Option 1 (Backend/Frontend Split)
2. Both work in the same repository on the same branch

### During Development
1. **Agent 1**: Commit backend services as they're completed (small, frequent commits)
2. **Agent 2**: Pull Agent 1's commits occasionally to see API response formats
3. **Agent 2**: Can mock API responses initially, then switch to real API once Agent 1's endpoints are ready
4. **Both**: Commit independently - no conflicts expected

### Integration Testing
1. Agent 1: Ensure all backend endpoints are tested and working
2. Agent 2: Pull latest from Agent 1, test frontend against real backend
3. Both: Run full integration test together

---

## Testing Strategy

### Agent 1 (Backend)
- Unit tests for each service (wwc_assessor, meta_analyzer, visualizer, conflict_detector)
- API endpoint tests with curl/Postman
- Manual testing checkpoints from guide

### Agent 2 (Frontend)
- Component rendering tests (can mock API responses)
- Integration tests once Agent 1's API is ready
- Manual testing in browser

### Integration Testing (After Both Complete)
- Full workflow: Select papers → WWC assessment → Meta-analysis → View results
- Test error handling
- Test edge cases

---

## Estimated Timeline

**Option 1 (Backend/Frontend Split)**:
- Agent 1 (Backend): 8-12 hours
- Agent 2 (Frontend): 10-14 hours
- **Total**: 18-26 hours (can be done in parallel, so ~12-14 hours wall time)

**Option 2 (Feature Split)**:
- Agent 1 (WWC): 6-8 hours
- Agent 2 (Synthesis): 12-18 hours
- **Total**: 18-26 hours (can be done in parallel, so ~12-18 hours wall time)

**Option 3 (Service/UI Split)**:
- Agent 1 (Services): 8-12 hours
- Agent 2 (UI): 10-14 hours
- **Total**: 18-26 hours (can be done in parallel, so ~12-14 hours wall time)

---

## Final Recommendation

**Use Option 1 (Backend/Frontend Split)** because:
1. Cleanest separation of concerns
2. Minimal file conflicts
3. Natural workflow (backend first, frontend consumes)
4. Easy to test independently
5. Clear ownership boundaries

**Setup**:
```bash
# Both agents work in the same repository
cd /path/to/jupyterlab-research-assistant-wwc-copilot
# Install dependencies, set up environment
pip install -e ".[dev,test]"
jlpm install
```

**Workflow**:
- Agent 1 commits backend API endpoints as they're ready
- Agent 2 pulls occasionally to see API response formats
- Agent 2 can start with mocked responses, then switch to real API
- Both commit independently - no conflicts since files don't overlap

