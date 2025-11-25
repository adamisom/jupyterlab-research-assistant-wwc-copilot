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

