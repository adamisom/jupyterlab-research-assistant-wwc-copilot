# Stage 2 Remaining Work

**Date**: Created after frontend Stage 2 implementation review  
**Purpose**: Document remaining work items identified during frontend implementation review

---

## Export Functionality for Synthesis Results

### Status: ⚠️ **MISSING** - Backend Implementation Required

### Source Reference
- **master-plan.md** (line 690): Lists "Export Functionality" as part of Synthesis Dashboard:
  > "4. **Export Functionality**: Buttons to export the comparison matrix as a CSV and the synthesis dashboard as a Markdown report."

- **stage-2-implementation-guide.md** (line 2084): Lists under "Remaining Stage 2 Enhancements":
  > "4. **Export Reports**: Generate Markdown/PDF synthesis reports"

### What's Missing

#### 1. Backend API Endpoints (Agent 1 - Backend)

**Endpoint 1: Export Meta-Analysis as CSV**
- **Route**: `POST /jupyterlab-research-assistant-wwc-copilot/meta-analysis/export`
- **Request Body**:
  ```json
  {
    "paper_ids": [1, 2, 3],
    "outcome_name": "optional_outcome_name"
  }
  ```
- **Response**: CSV file download
- **Content**: Comparison matrix with:
  - Paper titles/IDs
  - Effect sizes
  - Confidence intervals
  - Weights
  - Pooled effect
  - Heterogeneity statistics

**Endpoint 2: Export Synthesis Report as Markdown**
- **Route**: `POST /jupyterlab-research-assistant-wwc-copilot/synthesis/export`
- **Request Body**:
  ```json
  {
    "paper_ids": [1, 2, 3],
    "include_meta_analysis": true,
    "include_conflicts": true,
    "include_wwc_assessments": false  // Optional: include WWC ratings if available
  }
  ```
- **Response**: Markdown file download
- **Content**: Full synthesis report including:
  - Executive summary
  - Meta-analysis results (pooled effect, CI, heterogeneity)
  - Forest plot (as embedded image or reference)
  - Conflict detection results
  - Individual study details
  - References/bibliography

#### 2. Backend Service Functions (Agent 1 - Backend)

**File**: `jupyterlab_research_assistant_wwc_copilot/services/export_formatter.py` (extend existing)

Add methods:
- `export_meta_analysis_csv(meta_analysis_result: Dict, studies: List[Dict]) -> str`
- `export_synthesis_markdown(meta_analysis_result: Dict, conflict_result: Dict, papers: List[Dict]) -> str`

#### 3. Frontend API Client Functions (Already Implemented Structure)

**File**: `src/api.ts` (add these functions)

```typescript
export async function exportMetaAnalysis(
  paperIds: number[],
  outcomeName?: string
): Promise<void> {
  // Similar pattern to exportLibrary()
  // POST to meta-analysis/export endpoint
  // Trigger file download
}

export async function exportSynthesisReport(
  paperIds: number[],
  options?: {
    includeMetaAnalysis?: boolean;
    includeConflicts?: boolean;
    includeWWCAssessments?: boolean;
  }
): Promise<void> {
  // POST to synthesis/export endpoint
  // Trigger file download
}
```

#### 4. Frontend UI Buttons (Frontend - Already Has Structure)

**File**: `src/widgets/SynthesisWorkbench.tsx`

Add export buttons in the actions section:
- "Export Meta-Analysis (CSV)" button
- "Export Synthesis Report (Markdown)" button

**File**: `src/widgets/MetaAnalysisView.tsx`

Add export button in the view:
- "Export as CSV" button

---

## Implementation Notes

### CSV Export Format
Should include:
- Study identifier (title or ID)
- Effect size (d)
- Standard error
- 95% CI lower bound
- 95% CI upper bound
- Weight (%)
- Pooled effect row
- Summary statistics (I², tau², Q statistic)

### Markdown Export Format
Should be a comprehensive report with:
- Title: "Synthesis Report: [Topic/Date]"
- Introduction section
- Methods section (meta-analysis method, conflict detection method)
- Results section:
  - Meta-analysis summary
  - Forest plot (embedded base64 image or file reference)
  - Individual study results table
  - Conflict detection results
- Discussion section (optional, template)
- References section (formatted bibliography)

### Integration Points
- Export buttons should be in `SynthesisWorkbench` component
- Should use existing `exportLibrary()` pattern for file download
- Should handle errors gracefully with user notifications
- Should show loading state during export generation

---

## Priority

**Medium Priority** - Listed in master-plan as core feature, but also listed in "Remaining Enhancements" section. Should be implemented to complete Stage 2 as specified in master-plan.

---

## Dependencies

- ✅ Meta-analysis backend complete (required)
- ✅ Conflict detection backend complete (required)
- ✅ Forest plot generation complete (required)
- ⚠️ Export formatter service needs extension (to be implemented)

---

## Testing Checklist

When implemented, test:
- [ ] CSV export downloads correctly
- [ ] CSV contains all expected columns and data
- [ ] Markdown export downloads correctly
- [ ] Markdown is properly formatted and readable
- [ ] Forest plot image is embedded or referenced correctly in Markdown
- [ ] Export works with 2+ papers
- [ ] Export handles errors gracefully (missing data, network errors)
- [ ] Export buttons are visible and functional in UI
- [ ] File names are descriptive (include date/timestamp)

---

## Optional Stage 2 Enhancements

### Status: 📋 **OPTIONAL** - Future Enhancements

### Source Reference
- **stage-2-implementation-guide.md** (lines 2081-2086): Lists as "Remaining Stage 2 Enhancements"

### Enhancement List

#### 1. Enhanced WWC UI
**Description**: Improve the WWC Co-Pilot interface with a multi-step wizard, progress indicators, and ability to save/load assessments.

**Components Needed**:
- Multi-step wizard UI (step 1: randomization, step 2: attrition, step 3: baseline equivalence, etc.)
- Progress indicator showing current step
- Save/load assessment state (localStorage or backend)
- Resume incomplete assessments

**Files to Modify/Create**:
- `src/widgets/WWCCoPilot.tsx` (refactor to wizard format)
- Backend: Assessment storage endpoint (optional)

**Priority**: Medium - Improves UX but current implementation is functional

---

#### 2. Subgroup Analysis
**Description**: Perform meta-analysis by moderator variables (e.g., age group, intervention type, learning domain).

**Components Needed**:
- UI for selecting moderator variables
- Backend: Subgroup meta-analysis calculations
- Display: Separate forest plots or tables for each subgroup
- Statistical tests for subgroup differences

**Files to Modify/Create**:
- Backend: `services/meta_analyzer.py` (add subgroup methods)
- Backend: `routes.py` (add subgroup endpoint)
- Frontend: `src/api.ts` (add subgroup API function)
- Frontend: `src/widgets/MetaAnalysisView.tsx` (add subgroup display)
- Frontend: `src/widgets/SynthesisWorkbench.tsx` (add subgroup selector)

**Priority**: High - Common requirement in education meta-analysis

---

#### 3. Publication Bias Assessment
**Description**: Detect publication bias using funnel plots and Egger's test.

**Components Needed**:
- Backend: Funnel plot generation (effect size vs. standard error)
- Backend: Egger's test calculation
- Frontend: Funnel plot visualization
- Frontend: Bias assessment display

**Files to Modify/Create**:
- Backend: `services/visualizer.py` (add funnel plot method)
- Backend: `services/meta_analyzer.py` (add Egger's test)
- Backend: `routes.py` (add bias assessment endpoint)
- Frontend: `src/api.ts` (add bias assessment function)
- Frontend: `src/widgets/MetaAnalysisView.tsx` (add funnel plot display)

**Priority**: High - Standard practice in meta-analysis

---

#### 4. Advanced Conflict Detection
**Description**: Use AI extraction to identify key findings more accurately, rather than simple keyword-based extraction.

**Components Needed**:
- Backend: AI extraction of key findings from paper text
- Backend: Improved NLI model usage for finding comparison
- Frontend: Display extracted findings before conflict detection
- Frontend: Allow user to review/edit extracted findings

**Files to Modify/Create**:
- Backend: `services/conflict_detector.py` (improve `extract_key_findings()`)
- Backend: Integration with AI extraction service
- Frontend: `src/widgets/ConflictView.tsx` (show findings preview)

**Priority**: Medium - Improves accuracy but current implementation works

---

#### 5. Sensitivity Analysis
**Description**: Leave-one-out analysis and influence diagnostics to identify studies that heavily influence results.

**Components Needed**:
- Backend: Leave-one-out meta-analysis calculations
- Backend: Influence diagnostics (Cook's distance, etc.)
- Frontend: Display sensitivity results
- Frontend: Highlight influential studies

**Files to Modify/Create**:
- Backend: `services/meta_analyzer.py` (add sensitivity methods)
- Backend: `routes.py` (add sensitivity endpoint)
- Frontend: `src/api.ts` (add sensitivity function)
- Frontend: `src/widgets/MetaAnalysisView.tsx` (add sensitivity tab/section)

**Priority**: Medium - Useful for robustness checks

---

## Implementation Priority Summary

### High Priority (Core Meta-Analysis Features)
1. **Subgroup Analysis** - Essential for education research
2. **Publication Bias Assessment** - Standard meta-analysis practice

### Medium Priority (UX Improvements)
3. **Export Reports** - Documented above
4. **Enhanced WWC UI** - Improves workflow but not blocking
5. **Sensitivity Analysis** - Useful robustness check

### Lower Priority (Nice to Have)
6. **Advanced Conflict Detection** - Current implementation functional, AI extraction would improve accuracy

---

## Notes

- These enhancements can be implemented incrementally after core Stage 2 is complete
- Some enhancements (subgroup analysis, publication bias) are more critical for education research use cases
- Consider user feedback to prioritize which enhancements to implement first
- Each enhancement should be tested independently and can be released as separate features

