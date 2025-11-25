# Testing Guide

**Setup:**
- Build: `jlpm build`
- Install/update (one-time): `pip install -e . && jupyter labextension develop . --overwrite`
- Restart: `jupyter lab`

## Quick Smoke Test

**Minimum viable test (5 minutes):**
1. Open Research Library panel
2. Search and import 1 paper from Semantic Scholar
3. Import 1 PDF via file picker
4. Open paper detail view
5. Run WWC Co-Pilot assessment
6. Select 2 papers, open Synthesis Workbench
7. Run meta-analysis
8. Export synthesis report as Markdown
9. Check browser console for errors

---

## 1. Research Library & Discovery (Stage 1)

### Discovery Tab
- [ ] Search Semantic Scholar - results display correctly
- [ ] Search OpenAlex - results display correctly
- [ ] Fallback to OpenAlex when Semantic Scholar fails/rate-limited
- [ ] Import paper from search results - adds to library
- [ ] Error messages display if both providers fail

### Library Tab
- [ ] View all imported papers in list/grid
- [ ] Search library by title/author/keyword
- [ ] Filter papers (if applicable)
- [ ] Paper cards display: title, authors (as names, not [object Object]), year, citation count
- [ ] Paper cards have hover effects and left border accent
- [ ] Click paper card opens detail view
- [ ] Select multiple papers (checkbox selection)

### Paper Detail View
- [ ] All metadata displays: title, authors, year, DOI, abstract, citation count
- [ ] Study metadata displays (if available): methodology, sample sizes, effect sizes
- [ ] Learning science metadata displays (if available)
- [ ] "Open PDF" button works (if PDF available)
- [ ] "WWC Co-Pilot" button opens WWC assessment wizard
- [ ] "Synthesize" button appears when 2+ papers selected

### PDF Import
- [ ] File picker import - select PDF, verify import succeeds
- [ ] File browser context menu - right-click PDF, "Import to Research Library"
- [ ] PDF text extraction works
- [ ] Metadata extraction from PDF works (if AI configured)

### Library Export
- [ ] Export as JSON - file downloads, content correct
- [ ] Export as CSV - file downloads, content correct
- [ ] Export as BibTeX - file downloads, content correct
- [ ] Authors display correctly in all export formats

---

## 2. WWC Co-Pilot (Stage 2)

### Wizard Interface
- [ ] Multi-step wizard opens for selected paper
- [ ] Progress indicator/step counter visible
- [ ] All 5 steps accessible:
  - [ ] Step 1: Randomization
  - [ ] Step 2: Attrition
  - [ ] Step 3: Baseline Equivalence
  - [ ] Step 4: Statistical Adjustment
  - [ ] Step 5: Review & Finalize
- [ ] Navigation: Previous/Next buttons work
- [ ] Progress updates as steps completed

### Assessment Functionality
- [ ] Complete assessment for paper with full data
- [ ] Final rating displays on Review step
- [ ] WWC badge displays with correct color (green/yellow/red)
- [ ] Handle missing optional fields gracefully (no blank screen)
- [ ] Null/undefined values handled correctly (no console errors)
- [ ] Sections only appear when data available (graceful degradation)

### Integration
- [ ] Open from paper detail view
- [ ] Open from command palette
- [ ] WWC rating appears on paper cards after assessment

---

## 3. Synthesis Workbench (Stage 2)

### Opening Workbench
- [ ] Open with 2+ selected papers from library
- [ ] Command from command palette works
- [ ] Error if < 2 papers selected
- [ ] All tabs visible: Meta-Analysis, Conflict Detection, Subgroup Analysis, Bias Assessment, Sensitivity Analysis

### Meta-Analysis Tab
- [ ] Run meta-analysis with 2+ papers (with effect size data)
- [ ] Results display: pooled effect, CI, p-value, I², tau², Q statistic
- [ ] Forest plot displays correctly (base64 image)
- [ ] Individual studies table shows: effect size, CI, weight
- [ ] Stat cards display in grid layout with proper formatting
- [ ] Handle edge cases: 2 studies (no NaN values)
- [ ] Export as CSV - file downloads, content correct

### Conflict Detection Tab
- [ ] Run conflict detection with 2+ papers
- [ ] Key findings extracted for each paper
- [ ] Contradictions detected and displayed
- [ ] Each contradiction shows: paper titles, findings, confidence score
- [ ] Formatting clear and readable
- [ ] Contradictions highlighted/marked clearly

### Subgroup Analysis Tab
- [ ] Run with 3+ papers that have subgroup metadata
- [ ] Select subgroup variable (e.g., age_group, intervention_type)
- [ ] Results show separate meta-analyses for each subgroup
- [ ] Comparison statistics displayed
- [ ] Formatting correct

### Publication Bias Assessment Tab
- [ ] Run with 3+ papers
- [ ] Egger's test results display: p-value, interpretation
- [ ] Funnel plot displays correctly (effect sizes vs standard errors)
- [ ] Plot readable and properly formatted

### Sensitivity Analysis Tab
- [ ] Run with 2+ papers
- [ ] Leave-one-out analysis results display
- [ ] Results show how removing each study affects pooled effect
- [ ] Formatting correct

### Export Functionality
- [ ] Export synthesis report as Markdown - file downloads
- [ ] Markdown includes: meta-analysis results, conflicts (if run), references
- [ ] Authors display correctly in references (not dicts)
- [ ] Content matches what's displayed in workbench

---

## 4. Integration & Commands

### Command Palette
- [ ] "Open Research Library" command works
- [ ] "Import PDF" command works
- [ ] "Synthesize Studies" command works (with 2+ papers selected)
- [ ] "WWC Co-Pilot" command works (with 1 paper selected)

### File Browser Context Menu
- [ ] Right-click PDF shows "Import to Research Library"
- [ ] Import succeeds from context menu

### Events & Communication
- [ ] Paper selection events propagate correctly
- [ ] Library updates reflect in all views
- [ ] WWC assessment updates reflect on paper cards

---

## 5. UI/UX & Styling

### Visual Design
- [ ] All components styled with `jp-WWCExtension-*` classes
- [ ] Paper cards: left border accent, hover effects, transitions
- [ ] WWC badges: correct colors (green/yellow/red)
- [ ] Stat cards: grid layout, large bold values, brand color
- [ ] Buttons: smooth transitions, hover effects
- [ ] Tabs: smooth transitions, clear active state

### Theme Support
- [ ] Light theme: all colors readable, proper contrast
- [ ] Dark theme: all colors readable, proper contrast
- [ ] CSS variables adapt to theme correctly

### Navigation & Interactions
- [ ] Tab switching smooth (Synthesis Workbench)
- [ ] Step navigation smooth (WWC Co-Pilot)
- [ ] Loading states visible during operations
- [ ] Error messages display appropriately
- [ ] No unstyled elements

### Responsive Behavior
- [ ] Stat cards grid responsive
- [ ] Paper cards layout responsive
- [ ] All components usable at different window sizes

---

## 6. Error Handling & Edge Cases

### Data Validation
- [ ] Empty search results handled gracefully
- [ ] Missing paper data handled (no crashes)
- [ ] Invalid effect sizes handled in meta-analysis
- [ ] Missing optional fields handled (WWC Co-Pilot)

### API Failures
- [ ] Semantic Scholar rate limit → OpenAlex fallback
- [ ] Both providers fail → clear error message
- [ ] Network errors display user-friendly messages
- [ ] Backend errors display in UI (not just console)

### Edge Cases
- [ ] Meta-analysis with exactly 2 studies (no NaN)
- [ ] Papers with old author format (dict) display correctly
- [ ] Null/undefined values don't cause blank screens
- [ ] Empty library state handled
- [ ] No papers selected for synthesis → appropriate error

### Browser Console
- [ ] No JavaScript errors on page load
- [ ] No errors during normal operations
- [ ] No warnings about missing dependencies
- [ ] No TypeScript errors in console

---

## 7. Performance & Reliability

### Loading
- [ ] Extension loads quickly
- [ ] Large libraries (50+ papers) load without lag
- [ ] Search results load promptly
- [ ] Analysis operations show loading indicators

### Data Persistence
- [ ] Imported papers persist after restart
- [ ] WWC assessments persist after restart
- [ ] Library state persists

### Memory
- [ ] No memory leaks (check over extended use)
- [ ] Large PDFs don't crash extension
- [ ] Multiple analyses don't cause slowdown
