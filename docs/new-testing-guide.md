# New Testing Guide

**Standard Testing Steps (assumed for all commits):**
- Build: `jlpm build`
- Install/update extension: `pip install -e . && jupyter labextension develop . --overwrite`
- Restart JupyterLab: `jupyter lab`
- Verify extension loads: Check command palette for extension commands, check browser console for errors

---

## Commit: 7861317 - Add Export Functionality for Synthesis Results (Stage 2 Complete)

**Summary:** Added export functionality for meta-analysis and synthesis reports (CSV, Markdown).

**Testing:**
1. Open Synthesis Workbench with 2+ papers
2. Run meta-analysis
3. Look for export button or command
4. Export meta-analysis as CSV - verify file downloads
5. Export synthesis report as Markdown - verify file downloads
6. Open exported files and verify content is correct

---

## Commit: eeb40a4 - fix a build error

**Summary:** Fixed a build error.

**Testing:**
1. Build: `jlpm build`
2. Verify build completes without errors
3. Restart JupyterLab and verify extension loads

---

## Commit: 28a99a2 - Add work distribution summary to enhancements guide

**Summary:** Added work distribution documentation.

**Testing:** Documentation only - N/A

---

## Commit: c8163a5 - Fix frontend lint issues

**Summary:** Fixed frontend linting issues.

**Testing:**
1. Build: `jlpm build`
2. Verify build completes without lint errors
3. Restart JupyterLab and verify extension works

---

## Commit: f4be702 - Implement refactorings #1, 2, 3, 6, 8, 9, 10, 11, 14, 15

**Summary:** Implemented multiple refactorings for code quality improvements.

**Testing:**
1. Test all major functionality to ensure refactoring didn't break anything:
   - Research Library panel opens
   - Discovery search works
   - Library view and search work
   - Import/export work
   - WWC Co-Pilot works
   - Synthesis Workbench works
   - Meta-analysis works
   - Conflict detection works
2. Check browser console for errors

---

## Commit: 9996b0d - feat(frontend): Add API functions for Stage 2 enhancements

**Summary:** Added TypeScript API functions for subgroup analysis, bias assessment, and sensitivity analysis.

**Testing:**
1. Build frontend: `jlpm build`
2. Verify no TypeScript compilation errors
3. Restart JupyterLab and verify extension loads
4. (Functions won't be callable until backend routes added - just verify no build errors)

---

## Commit: dd0b53d - feat(frontend): Add new analysis view components

**Summary:** Added SubgroupAnalysisView, BiasAssessmentView, and SensitivityAnalysisView components.

**Testing:**
1. Components won't be accessible until integrated into Synthesis Workbench
2. Verify no build errors
3. Check browser console for component loading

---

## Commit: 38dad65 - feat(frontend): Integrate Stage 2 enhancements into Synthesis Workbench

**Summary:** Integrated subgroup analysis, bias assessment, and sensitivity analysis into Synthesis Workbench.

**Testing:**
1. Open Synthesis Workbench with 3+ papers
2. Verify new tabs/sections appear for:
   - Subgroup Analysis
   - Publication Bias Assessment
   - Sensitivity Analysis
3. Check that tabs are accessible and UI renders correctly

---

## Commit: fd4a16a - feat(frontend): Add CSS styles for Stage 2 enhancements

**Summary:** Added CSS styling for new analysis view components.

**Testing:**
1. Open Synthesis Workbench
2. Navigate to each new analysis tab
3. Verify styling looks correct and consistent with rest of UI
4. Check layout and responsive behavior

---

## Commit: 1bb11a6 - feat: add scipy dependency for statistical tests

**Summary:** Added scipy dependency for statistical calculations.

**Testing:**
1. Verify scipy is installed: `pip list | grep scipy`
2. Test statistical features (meta-analysis, bias assessment) to ensure scipy integration works

---

## Commit: c7f4eb8 - feat: implement subgroup analysis for meta-analysis

**Summary:** Implemented subgroup analysis backend logic.

**Testing:**
1. Test subgroup analysis endpoint via API:
   - POST to `/jupyterlab-research-assistant-wwc-copilot/subgroup-analysis`
   - Send JSON with `paper_ids`, `subgroup_variable` (e.g., "age_group"), and optional `outcome_name`
   - Verify response contains subgroup results with comparisons
2. Or test via Synthesis Workbench Subgroup Analysis tab
3. Verify results show separate meta-analyses for each subgroup and comparison statistics

---

## Commit: 154eab5 - feat: add subgroup analysis API endpoint and tests

**Summary:** Added API route handler for subgroup analysis endpoint.

**Testing:**
1. Open Synthesis Workbench with 3+ papers that have subgroup metadata
2. Go to Subgroup Analysis tab
3. Select a subgroup variable (e.g., "age_group", "intervention_type")
4. Run subgroup analysis
5. Verify results display with subgroup breakdowns and comparison statistics

---

## Commit: c86c1c9 - feat: implement publication bias assessment (Egger's test and funnel plots)

**Summary:** Implemented publication bias assessment backend with Egger's test and funnel plot generation.

**Testing:**
1. Test bias assessment endpoint via API:
   - POST to `/jupyterlab-research-assistant-wwc-copilot/bias-assessment`
   - Send JSON with `paper_ids` (at least 3) and optional `outcome_name`
   - Verify response contains Egger's test results and funnel plot (base64 image)
2. Or test via Synthesis Workbench Bias Assessment tab
3. Verify Egger's test results display with interpretation
4. Verify funnel plot displays correctly

---

## Commit: 9e2c15a - feat: add publication bias assessment API endpoint and tests

**Summary:** Added API route handler for publication bias assessment endpoint.

**Testing:**
1. Open Synthesis Workbench with 3+ papers
2. Go to Publication Bias Assessment tab
3. Run bias assessment
4. Verify Egger's test results appear with p-value and interpretation
5. Verify funnel plot displays with effect sizes vs standard errors
6. Check that plot is readable and properly formatted

---

## Commit: a1ff311 - feat: enhance conflict detection with AI-powered finding extraction

**Summary:** Enhanced conflict detection to extract key findings using AI before detecting contradictions.

**Testing:**
1. Open Synthesis Workbench with 2+ papers
2. Go to Conflict Detection tab
3. Run conflict detection
4. Verify that findings are extracted for each paper
5. Verify contradictions are detected and displayed
6. Check that findings are shown alongside contradictions for context

---

## Commit: 5018c08 - feat: add TypeScript interfaces for Stage 2 enhancement APIs

**Summary:** Added TypeScript type definitions for Stage 2 enhancement API responses.

**Testing:**
1. Build frontend: `jlpm build`
2. Verify no TypeScript compilation errors
3. Restart JupyterLab and verify extension loads
4. (Type safety improvement - verify no runtime errors related to type mismatches)

---

## Commit: f15c0ad - feat: refactor WWC Co-Pilot to multi-step wizard interface

**Summary:** Refactored WWC Co-Pilot from single view to multi-step wizard with progress indicator.

**Testing:**
1. Open WWC Co-Pilot for a paper
2. Verify it shows a multi-step wizard interface with:
   - Progress bar or step indicator
   - Step 1: Randomization
   - Step 2: Attrition
   - Step 3: Baseline Equivalence
   - Step 4: Statistical Adjustment
   - Step 5: Review & Finalize
3. Verify you can navigate between steps with Previous/Next buttons
4. Verify progress indicator updates as you move through steps
5. Complete all steps and run assessment
6. Verify final rating displays on review step

---

## Commit: 15914a1 - feat: update SubgroupAnalysisView component formatting

**Summary:** Updated formatting and display of subgroup analysis results.

**Testing:**
1. Open Synthesis Workbench
2. Run subgroup analysis
3. Verify results are properly formatted and readable
4. Check that subgroup comparisons are clearly displayed
5. Verify numbers are formatted correctly (decimals, percentages, etc.)

---

## Commit: 86df61d - feat: update analysis view components formatting

**Summary:** Updated formatting for multiple analysis view components.

**Testing:**
1. Open Synthesis Workbench
2. Test each analysis view:
   - Meta-Analysis: Verify formatting looks good
   - Conflict Detection: Verify formatting looks good
   - Subgroup Analysis: Verify formatting looks good
   - Bias Assessment: Verify formatting looks good
   - Sensitivity Analysis: Verify formatting looks good
3. Check that all numbers, labels, and results are properly formatted

---

## Commit: 6e0004b - feat: update ConflictView component formatting

**Summary:** Updated formatting for conflict detection results display.

**Testing:**
1. Open Synthesis Workbench
2. Run conflict detection
3. Verify conflicts are clearly displayed with proper formatting
4. Check that paper titles, findings, and confidence scores are readable
5. Verify contradictions are highlighted or clearly marked

---

## Commit: f8eb8fa - feat: integrate Stage 2 enhancements into Synthesis Workbench

**Summary:** Integrated all Stage 2 enhancements (subgroup, bias, sensitivity) into Synthesis Workbench tabs.

**Testing:**
1. Open Synthesis Workbench with 3+ papers
2. Verify all tabs are present and accessible:
   - Meta-Analysis
   - Conflict Detection
   - Subgroup Analysis
   - Publication Bias Assessment
   - Sensitivity Analysis
3. Test each tab:
   - Navigate to each tab
   - Run the analysis (if applicable)
   - Verify results display correctly
   - Verify you can switch between tabs smoothly

---

## Commit: 2197668 - fix: Add OpenAlex API client as fallback for paper discovery

**Summary:** Added OpenAlex API client with search_papers and get_paper_details methods. Transforms OpenAlex format to match Semantic Scholar format.

**Testing:**
1. Test discovery search - should work with both Semantic Scholar and OpenAlex
2. Verify OpenAlex results display correctly (authors, titles, abstracts)
3. Check that OpenAlex format is properly transformed to match expected structure

---

## Commit: e42b81a - fix: Remove unsupported year parameter from Semantic Scholar API

**Summary:** Removed unsupported year parameter that was causing 400 errors in Semantic Scholar API calls.

**Testing:**
1. Test discovery search with year filter
2. Verify search completes without 400 errors
3. Check that results are still returned (year filtering may need to be done client-side)

---

## Commit: bf3a3fd - fix: Add OpenAlex fallback to discovery handler

**Summary:** Added automatic fallback to OpenAlex when Semantic Scholar fails (e.g., rate limits).

**Testing:**
1. Test discovery search when Semantic Scholar is unavailable or rate-limited
2. Verify automatic fallback to OpenAlex works
3. Check that error messages are clear if both providers fail
4. Verify consistent response format regardless of which provider is used

---

## Commit: 2be02d5 - fix: Normalize authors to strings in database layer

**Summary:** Normalizes authors to strings when storing and retrieving papers. Fixes [object Object] display issue in UI.

**Testing:**
1. Import a paper (from Semantic Scholar or OpenAlex)
2. View paper in library - authors should display as names, not [object Object]
3. Check detail view - authors should display correctly
4. Verify backwards compatibility with existing papers that may have old format

---

## Commit: aa0f11d - fix: Update DiscoveryTab placeholder to mention both providers

**Summary:** Updated search input placeholder to mention both Semantic Scholar and OpenAlex.

**Testing:**
1. Open Research Library panel
2. Go to Discovery tab
3. Verify placeholder text mentions both providers (e.g., "Search Semantic Scholar / OpenAlex...")

---

## Commit: ed80a1e - fix: Add robust NaN handling in meta-analysis

**Summary:** Added comprehensive NaN/infinity handling for edge cases in meta-analysis, especially with 2 studies.

**Testing:**
1. Run meta-analysis with exactly 2 papers that have effect size data
2. Verify results display correctly (no NaN values)
3. Check that confidence intervals, p-values, and tau_squared are valid numbers
4. Verify meta-analysis completes without errors even with edge case data

---

## Commit: d75f38a - fix: Fix WWC Co-Pilot null value handling

**Summary:** Fixed null checks to handle both null and undefined values. Prevents blank screen when backend returns null for optional fields.

**Testing:**
1. Open WWC Co-Pilot for a paper
2. Run assessment with missing optional fields (baseline_effect_size, attrition values)
3. Verify widget displays correctly (no blank screen)
4. Check that sections only appear when data is available (graceful degradation)
5. Verify no browser console errors about null values

---

## Commit: eb84b44 - fix: Make Synthesis Workbench command silently return when called without args

**Summary:** Command now silently returns when called without paperIds (e.g., from command palette or layout restorer), preventing error modals on page refresh.

**Testing:**
1. Refresh browser (Cmd+R / Ctrl+R)
2. Verify no error modal appears about "Please select at least 2 papers"
3. Open Synthesis Workbench normally with 2+ papers - should work as before
4. Try calling command from command palette without selecting papers - should silently return

---

## Commit: d332fff - Implement Phase 1 styling improvements

**Summary:** Replaced hardcoded colors with CSS variables, moved inline styles to CSS classes, added elevation variables, enhanced paper cards with transitions and hover effects, added WWC badge styling.

**Testing:**
1. Open Research Library panel
2. Verify paper cards have left border accent and smooth hover effects
3. Check WWC badges display with correct colors (green/yellow/red for different ratings)
4. Verify all colors adapt to light/dark theme
5. Check that buttons and interactive elements have smooth transitions
6. Verify stat cards have proper elevation and visual hierarchy

---

## Commit: 6c02e1f - Implement Phase 2 structural styling improvements

**Summary:** Reorganized CSS files, improved stat cards with grid layout, enhanced transitions on all interactive elements.

**Testing:**
1. Open Synthesis Workbench
2. Run meta-analysis
3. Verify stat cards display in grid layout (responsive)
4. Check that stat values are large, bold, and in brand color
5. Verify tabs, buttons, and inputs have smooth transitions
6. Check that stat cards have hover effects (elevation change, slight translateY)

---

## Commit: 8bd8512 - Implement Phase 3.1: Refactor CSS class names

**Summary:** Refactored all CSS class names from `jp-jupyterlab-research-assistant-wwc-copilot-*` to shorter `jp-WWCExtension-*` format.

**Testing:**
1. Open Research Library panel - verify all styling still works
2. Open Synthesis Workbench - verify all styling still works
3. Open WWC Co-Pilot - verify all styling still works
4. Check all tabs, buttons, cards, and components render correctly
5. Verify no unstyled elements (should look identical to before, just with new class names)
6. Test in both light and dark themes

---

## Testing Checklist Summary

After testing all commits, verify the complete system works end-to-end:

1. **Stage 1 Features:**
   - [ ] Semantic Scholar discovery and search
   - [ ] PDF import (file picker and context menu)
   - [ ] Library view with search and filtering
   - [ ] Paper detail view
   - [ ] Export library (JSON, CSV, BibTeX)

2. **Stage 2 Core Features:**
   - [ ] WWC Co-Pilot wizard (all 5 steps)
   - [ ] Meta-analysis with forest plot
   - [ ] Conflict detection with findings

3. **Stage 2 Enhancements:**
   - [ ] Subgroup analysis
   - [ ] Publication bias assessment (Egger's test, funnel plot)
   - [ ] Sensitivity analysis (leave-one-out)

4. **Integration:**
   - [ ] Commands work from command palette
   - [ ] File browser context menu works
   - [ ] Events between components work
   - [ ] Export functionality works for all formats

5. **UI/UX:**
   - [ ] All components styled correctly
   - [ ] Navigation works smoothly
   - [ ] Error messages display appropriately
   - [ ] Loading states show during operations
