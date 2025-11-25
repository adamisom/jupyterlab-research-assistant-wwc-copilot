# Stage 2 Enhancements Implementation Guide

**Purpose**: Step-by-step implementation guide for optional Stage 2 enhancements.

**⚠️ Prerequisites**: Stage 2 core features (WWC assessment, meta-analysis, conflict detection) must be 100% complete before starting enhancements.

**Project Name**: `jupyterlab-research-assistant-wwc-copilot`  
**Python Package**: `jupyterlab_research_assistant_wwc_copilot`  
**Plugin ID**: `jupyterlab-research-assistant-wwc-copilot:plugin`  
**API Route Prefix**: `/jupyterlab-research-assistant-wwc-copilot`

---

## Work Distribution Summary

### For Agent 1 (Backend)

**Primary Responsibilities**:
- Implement backend service methods for statistical calculations
- Create API endpoints (route handlers)
- Extend existing services (meta_analyzer, visualizer, conflict_detector)
- Database operations (if needed for storage features)

**Files to Modify/Create**:
- `jupyterlab_research_assistant_wwc_copilot/services/meta_analyzer.py` - Add subgroup analysis, Egger's test, sensitivity analysis methods
- `jupyterlab_research_assistant_wwc_copilot/services/visualizer.py` - Add funnel plot generation
- `jupyterlab_research_assistant_wwc_copilot/services/conflict_detector.py` - Enhance finding extraction with AI
- `jupyterlab_research_assistant_wwc_copilot/routes.py` - Add API handlers for all enhancements
- `jupyterlab_research_assistant_wwc_copilot/services/export_formatter.py` - (Already completed)

**Enhancements Requiring Backend Work**:
1. ✅ **Enhanced WWC UI** - Optional assessment storage endpoint (or use frontend localStorage)
2. ✅ **Subgroup Analysis** - Service method + API endpoint
3. ✅ **Publication Bias Assessment** - Egger's test + funnel plot + API endpoint
4. ✅ **Advanced Conflict Detection** - AI extraction integration
5. ✅ **Sensitivity Analysis** - Service method + API endpoint

**Dependencies to Add** (if not already present):
- `scipy` - For statistical tests (Egger's test)
- `numpy` - For array operations (already used)

---

### For Agent 2 (Frontend)

**Primary Responsibilities**:
- Create/update React components for new UI features
- Add API client functions to call backend endpoints
- Implement UI interactions and state management
- Add CSS styling for new components
- Integrate new features into existing widgets

**Files to Modify/Create**:
- `src/api.ts` - Add API client functions for all enhancements
- `src/widgets/WWCCoPilot.tsx` - Refactor to multi-step wizard (Enhanced WWC UI)
- `src/widgets/SynthesisWorkbench.tsx` - Add buttons/controls for new analyses
- `src/widgets/SubgroupAnalysisView.tsx` - NEW component
- `src/widgets/BiasAssessmentView.tsx` - NEW component
- `src/widgets/SensitivityAnalysisView.tsx` - NEW component
- `src/widgets/ConflictView.tsx` - Add findings preview (Advanced Conflict Detection)
- `style/index.css` - Add styles for wizard, new views, etc.

**Enhancements Requiring Frontend Work**:
1. ✅ **Enhanced WWC UI** - Multi-step wizard component, progress indicators, save/load UI
2. ✅ **Subgroup Analysis** - Subgroup selector, results display component
3. ✅ **Publication Bias Assessment** - Bias assessment button, results display
4. ✅ **Advanced Conflict Detection** - Findings preview UI (backend does AI extraction)
5. ✅ **Sensitivity Analysis** - Sensitivity analysis button, results display

**Integration Points**:
- All new features integrate into `SynthesisWorkbench` widget
- Enhanced WWC UI replaces existing `WWCCoPilot` component
- New analysis views can be added as tabs or sections in Synthesis Workbench

---

## Table of Contents

1. [Enhanced WWC UI](#enhanced-wwc-ui)
2. [Subgroup Analysis](#subgroup-analysis)
3. [Publication Bias Assessment](#publication-bias-assessment)
4. [Advanced Conflict Detection](#advanced-conflict-detection)
5. [Sensitivity Analysis](#sensitivity-analysis)

---

## Enhanced WWC UI

### Overview
Transform the WWC Co-Pilot from a single-form interface into a multi-step wizard with progress indicators and save/load functionality.

### Backend Changes

#### Phase 1: Assessment Storage (Optional)
**File**: `jupyterlab_research_assistant_wwc_copilot/routes.py`

Add handler for saving/loading assessments:

```python
class WWCAssessmentStorageHandler(APIHandler):
    """Handler for saving and loading WWC assessments."""
    
    @tornado.web.authenticated
    def post(self):
        """Save an assessment."""
        try:
            data = self.get_json_body()
            paper_id = data.get("paper_id")
            assessment_data = data.get("assessment_data")
            
            # Store in database or file system
            # Implementation depends on storage strategy
            # Could add assessment table to database
            
            self.finish(json.dumps({
                "status": "success",
                "message": "Assessment saved"
            }))
        except Exception as e:
            self.set_status(500)
            self.finish(json.dumps({
                "status": "error",
                "message": str(e)
            }))
    
    @tornado.web.authenticated
    def get(self):
        """Load a saved assessment."""
        try:
            paper_id = self.get_argument("paper_id")
            
            # Retrieve from database or file system
            assessment_data = {}  # Load from storage
            
            self.finish(json.dumps({
                "status": "success",
                "data": assessment_data
            }))
        except Exception as e:
            self.set_status(500)
            self.finish(json.dumps({
                "status": "error",
                "message": str(e)
            }))
```

**Alternative**: Use browser localStorage (frontend-only, no backend needed)

### Frontend Changes

#### Phase 2: Multi-Step Wizard Component
**File**: `src/widgets/WWCCoPilot.tsx` (refactor)

```typescript
import React, { useState, useEffect } from 'react';
import { runWWCAssessment, IWWCAssessment, IWWCAssessmentRequest } from '../api';
import { showErrorMessage } from '@jupyterlab/apputils';

interface WWCCoPilotProps {
  paperId: number;
  paperTitle: string;
  onClose?: () => void;
}

type WizardStep = 'randomization' | 'attrition' | 'baseline' | 'adjustment' | 'review';

export const WWCCoPilot: React.FC<WWCCoPilotProps> = ({
  paperId,
  paperTitle,
  onClose
}) => {
  const [currentStep, setCurrentStep] = useState<WizardStep>('randomization');
  const [assessment, setAssessment] = useState<IWWCAssessment | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [judgments, setJudgments] = useState<IWWCAssessmentRequest['judgments']>({
    chosen_attrition_boundary: 'cautious',
    adjustment_strategy_is_valid: undefined,
    randomization_documented: undefined
  });

  const steps: WizardStep[] = ['randomization', 'attrition', 'baseline', 'adjustment', 'review'];
  const stepLabels = {
    randomization: 'Randomization',
    attrition: 'Attrition',
    baseline: 'Baseline Equivalence',
    adjustment: 'Statistical Adjustment',
    review: 'Review & Finalize'
  };

  const getStepIndex = (step: WizardStep): number => steps.indexOf(step);
  const progress = ((getStepIndex(currentStep) + 1) / steps.length) * 100;

  useEffect(() => {
    // Load saved assessment from localStorage
    const saved = localStorage.getItem(`wwc-assessment-${paperId}`);
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        setJudgments(parsed.judgments || judgments);
        setCurrentStep(parsed.currentStep || 'randomization');
      } catch (e) {
        console.error('Failed to load saved assessment:', e);
      }
    }
  }, [paperId]);

  const saveProgress = () => {
    localStorage.setItem(`wwc-assessment-${paperId}`, JSON.stringify({
      judgments,
      currentStep
    }));
  };

  const runAssessment = async () => {
    setIsLoading(true);
    try {
      const request: IWWCAssessmentRequest = {
        paper_id: paperId,
        judgments
      };
      const result = await runWWCAssessment(request);
      setAssessment(result);
      saveProgress();
    } catch (err) {
      showErrorMessage('WWC Assessment Error', err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleNext = () => {
    const currentIndex = getStepIndex(currentStep);
    if (currentIndex < steps.length - 1) {
      setCurrentStep(steps[currentIndex + 1]);
      saveProgress();
    }
  };

  const handlePrevious = () => {
    const currentIndex = getStepIndex(currentStep);
    if (currentIndex > 0) {
      setCurrentStep(steps[currentIndex - 1]);
    }
  };

  const handleStepChange = (step: WizardStep) => {
    setCurrentStep(step);
    saveProgress();
  };

  return (
    <div className="jp-jupyterlab-research-assistant-wwc-copilot-wwc">
      <div className="jp-jupyterlab-research-assistant-wwc-copilot-wwc-header">
        <h2>WWC Co-Pilot: {paperTitle}</h2>
        {onClose && (
          <button onClick={onClose} className="jp-jupyterlab-research-assistant-wwc-copilot-close">
            ×
          </button>
        )}
      </div>

      {/* Progress Indicator */}
      <div className="jp-jupyterlab-research-assistant-wwc-copilot-wwc-progress">
        <div className="jp-jupyterlab-research-assistant-wwc-copilot-wwc-progress-bar">
          <div
            className="jp-jupyterlab-research-assistant-wwc-copilot-wwc-progress-fill"
            style={{ width: `${progress}%` }}
          />
        </div>
        <div className="jp-jupyterlab-research-assistant-wwc-copilot-wwc-steps">
          {steps.map((step, idx) => (
            <button
              key={step}
              className={`jp-jupyterlab-research-assistant-wwc-copilot-step ${
                currentStep === step ? 'active' : ''
              } ${getStepIndex(currentStep) > idx ? 'completed' : ''}`}
              onClick={() => handleStepChange(step)}
            >
              <span className="step-number">{idx + 1}</span>
              <span className="step-label">{stepLabels[step]}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Step Content */}
      <div className="jp-jupyterlab-research-assistant-wwc-copilot-wwc-content">
        {currentStep === 'randomization' && (
          <RandomizationStep
            randomizationDocumented={judgments.randomization_documented}
            onChange={(value) => setJudgments({ ...judgments, randomization_documented: value })}
          />
        )}
        {currentStep === 'attrition' && (
          <AttritionStep
            boundary={judgments.chosen_attrition_boundary}
            onChange={(value) => setJudgments({ ...judgments, chosen_attrition_boundary: value })}
            assessment={assessment}
          />
        )}
        {currentStep === 'baseline' && (
          <BaselineStep assessment={assessment} />
        )}
        {currentStep === 'adjustment' && (
          <AdjustmentStep
            adjustmentValid={judgments.adjustment_strategy_is_valid}
            onChange={(value) => setJudgments({ ...judgments, adjustment_strategy_is_valid: value })}
          />
        )}
        {currentStep === 'review' && (
          <ReviewStep
            assessment={assessment}
            judgments={judgments}
            onRunAssessment={runAssessment}
            isLoading={isLoading}
          />
        )}
      </div>

      {/* Navigation Buttons */}
      <div className="jp-jupyterlab-research-assistant-wwc-copilot-wwc-navigation">
        <button
          onClick={handlePrevious}
          disabled={currentStep === steps[0]}
          className="jp-jupyterlab-research-assistant-wwc-copilot-button"
        >
          Previous
        </button>
        {currentStep !== steps[steps.length - 1] ? (
          <button
            onClick={handleNext}
            className="jp-jupyterlab-research-assistant-wwc-copilot-button"
          >
            Next
          </button>
        ) : (
          <button
            onClick={runAssessment}
            disabled={isLoading}
            className="jp-jupyterlab-research-assistant-wwc-copilot-button"
          >
            {isLoading ? 'Running...' : 'Run Assessment'}
          </button>
        )}
      </div>
    </div>
  );
};

// Individual step components (simplified examples)
const RandomizationStep: React.FC<{ randomizationDocumented?: boolean; onChange: (value: boolean) => void }> = ({ randomizationDocumented, onChange }) => (
  <div>
    <h3>Step 1: Randomization</h3>
    <p>Was randomization properly documented in the study?</p>
    <select
      value={randomizationDocumented === undefined ? '' : String(randomizationDocumented)}
      onChange={(e) => onChange(e.target.value === 'true')}
    >
      <option value="">Not specified</option>
      <option value="true">Yes</option>
      <option value="false">No</option>
    </select>
  </div>
);

const AttritionStep: React.FC<{ boundary: string; onChange: (value: string) => void; assessment: IWWCAssessment | null }> = ({ boundary, onChange, assessment }) => (
  <div>
    <h3>Step 2: Attrition</h3>
    <label>Attrition Boundary:</label>
    <select value={boundary} onChange={(e) => onChange(e.target.value)}>
      <option value="cautious">Cautious (default)</option>
      <option value="optimistic">Optimistic</option>
    </select>
    {assessment && (
      <div>
        <p>Overall Attrition: {(assessment.overall_attrition! * 100).toFixed(1)}%</p>
        <p>Differential Attrition: {(assessment.differential_attrition! * 100).toFixed(1)}%</p>
      </div>
    )}
  </div>
);

const BaselineStep: React.FC<{ assessment: IWWCAssessment | null }> = ({ assessment }) => (
  <div>
    <h3>Step 3: Baseline Equivalence</h3>
    {assessment?.baseline_effect_size !== undefined && (
      <p>Effect Size (Cohen's d): {assessment.baseline_effect_size.toFixed(3)}</p>
    )}
  </div>
);

const AdjustmentStep: React.FC<{ adjustmentValid?: boolean; onChange: (value: boolean) => void }> = ({ adjustmentValid, onChange }) => (
  <div>
    <h3>Step 4: Statistical Adjustment</h3>
    <p>Was a valid statistical adjustment used?</p>
    <select
      value={adjustmentValid === undefined ? '' : String(adjustmentValid)}
      onChange={(e) => onChange(e.target.value === 'true')}
    >
      <option value="">Not applicable</option>
      <option value="true">Yes</option>
      <option value="false">No</option>
    </select>
  </div>
);

const ReviewStep: React.FC<{
  assessment: IWWCAssessment | null;
  judgments: IWWCAssessmentRequest['judgments'];
  onRunAssessment: () => void;
  isLoading: boolean;
}> = ({ assessment, judgments, onRunAssessment, isLoading }) => (
  <div>
    <h3>Step 5: Review & Finalize</h3>
    <div>
      <h4>Your Judgments:</h4>
      <ul>
        <li>Attrition Boundary: {judgments.chosen_attrition_boundary}</li>
        <li>Randomization Documented: {judgments.randomization_documented?.toString() || 'Not specified'}</li>
        <li>Adjustment Valid: {judgments.adjustment_strategy_is_valid?.toString() || 'Not applicable'}</li>
      </ul>
    </div>
    {assessment && (
      <div>
        <h4>Final Rating: {assessment.final_rating}</h4>
        <ul>
          {assessment.rating_justification.map((reason, idx) => (
            <li key={idx}>{reason}</li>
          ))}
        </ul>
      </div>
    )}
  </div>
);
```

#### Phase 3: CSS Updates
**File**: `style/index.css`

Add styles for wizard components:

```css
/* WWC Wizard Progress Indicator */
.jp-jupyterlab-research-assistant-wwc-copilot-wwc-progress {
  margin-bottom: 24px;
}

.jp-jupyterlab-research-assistant-wwc-copilot-wwc-progress-bar {
  height: 4px;
  background-color: var(--jp-border-color2);
  border-radius: 2px;
  margin-bottom: 16px;
  overflow: hidden;
}

.jp-jupyterlab-research-assistant-wwc-copilot-wwc-progress-fill {
  height: 100%;
  background-color: var(--jp-brand-color1);
  transition: width 0.3s ease;
}

.jp-jupyterlab-research-assistant-wwc-copilot-wwc-steps {
  display: flex;
  justify-content: space-between;
  gap: 8px;
}

.jp-jupyterlab-research-assistant-wwc-copilot-step {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px;
  background: none;
  border: 2px solid var(--jp-border-color1);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.jp-jupyterlab-research-assistant-wwc-copilot-step.active {
  border-color: var(--jp-brand-color1);
  background-color: var(--jp-brand-color3);
}

.jp-jupyterlab-research-assistant-wwc-copilot-step.completed {
  border-color: var(--jp-success-color1);
  background-color: var(--jp-success-color3);
}

.jp-jupyterlab-research-assistant-wwc-copilot-step .step-number {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background-color: var(--jp-border-color2);
  color: var(--jp-content-font-color2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  margin-bottom: 4px;
}

.jp-jupyterlab-research-assistant-wwc-copilot-step.active .step-number {
  background-color: var(--jp-brand-color1);
  color: white;
}

.jp-jupyterlab-research-assistant-wwc-copilot-step.completed .step-number {
  background-color: var(--jp-success-color1);
  color: white;
}

.jp-jupyterlab-research-assistant-wwc-copilot-step .step-label {
  font-size: var(--jp-ui-font-size0);
  color: var(--jp-content-font-color2);
  text-align: center;
}

.jp-jupyterlab-research-assistant-wwc-copilot-wwc-navigation {
  display: flex;
  justify-content: space-between;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid var(--jp-border-color1);
}
```

---

## Subgroup Analysis

### Overview
Perform meta-analysis separately for different subgroups (e.g., by age group, intervention type, learning domain).

### Backend Changes

#### Phase 1: Subgroup Meta-Analysis Service
**File**: `jupyterlab_research_assistant_wwc_copilot/services/meta_analyzer.py`

Add subgroup analysis method:

```python
def perform_subgroup_meta_analysis(
    self,
    studies: List[Dict],
    subgroup_variable: str
) -> Dict:
    """
    Perform meta-analysis for each subgroup.
    
    Args:
        studies: List of study dictionaries with subgroup metadata
        subgroup_variable: Field name for subgroup (e.g., 'age_group', 'intervention_type')
    
    Returns:
        Dictionary with:
            - subgroups: Dict mapping subgroup name to meta-analysis results
            - overall: Overall meta-analysis (all studies combined)
            - subgroup_comparison: Test for differences between subgroups
    """
    # Group studies by subgroup
    subgroups = {}
    for study in studies:
        subgroup_value = study.get(subgroup_variable, 'unknown')
        if subgroup_value not in subgroups:
            subgroups[subgroup_value] = []
        subgroups[subgroup_value].append(study)
    
    # Perform meta-analysis for each subgroup
    subgroup_results = {}
    for subgroup_name, subgroup_studies in subgroups.items():
        if len(subgroup_studies) >= 2:
            result = self.perform_random_effects_meta_analysis(subgroup_studies)
            subgroup_results[subgroup_name] = result
    
    # Perform overall meta-analysis
    overall_result = self.perform_random_effects_meta_analysis(studies)
    
    # Test for subgroup differences (meta-regression or Q-between)
    # Implementation depends on statistical method chosen
    
    return {
        "subgroups": subgroup_results,
        "overall": overall_result,
        "subgroup_variable": subgroup_variable,
        "n_subgroups": len(subgroup_results)
    }
```

#### Phase 2: Subgroup API Endpoint
**File**: `jupyterlab_research_assistant_wwc_copilot/routes.py`

Add handler:

```python
class SubgroupAnalysisHandler(APIHandler):
    """Handler for subgroup meta-analysis."""
    
    @tornado.web.authenticated
    def post(self):
        """Perform subgroup meta-analysis."""
        try:
            data = self.get_json_body()
            paper_ids = data.get("paper_ids", [])
            subgroup_variable = data.get("subgroup_variable")  # e.g., "age_group"
            outcome_name = data.get("outcome_name")
            
            if not subgroup_variable:
                self.set_status(400)
                self.finish(json.dumps({
                    "status": "error",
                    "message": "subgroup_variable required"
                }))
                return
            
            # Fetch papers and extract subgroup metadata
            with DatabaseManager() as db:
                studies = []
                for paper_id in paper_ids:
                    paper = db.get_paper_by_id(paper_id)
                    if not paper:
                        continue
                    
                    # Extract effect sizes and subgroup value
                    effect_sizes = paper.get("study_metadata", {}).get("effect_sizes", {})
                    learning_metadata = paper.get("learning_science_metadata", {})
                    
                    # Get subgroup value from appropriate metadata field
                    subgroup_value = None
                    if subgroup_variable == "age_group":
                        subgroup_value = learning_metadata.get("age_group")
                    elif subgroup_variable == "intervention_type":
                        subgroup_value = learning_metadata.get("intervention_type")
                    # Add more mappings as needed
                    
                    if outcome_name and effect_sizes:
                        outcome_data = effect_sizes.get(outcome_name)
                        if outcome_data and subgroup_value:
                            studies.append({
                                "paper_id": paper["id"],
                                "study_label": paper["title"],
                                "effect_size": outcome_data.get("d", 0.0),
                                "std_error": outcome_data.get("se", 0.1),
                                subgroup_variable: subgroup_value
                            })
                
                if len(studies) < 2:
                    self.set_status(400)
                    self.finish(json.dumps({
                        "status": "error",
                        "message": "Insufficient studies with subgroup data"
                    }))
                    return
                
                # Perform subgroup analysis
                analyzer = MetaAnalyzer()
                result = analyzer.perform_subgroup_meta_analysis(studies, subgroup_variable)
                
                self.finish(json.dumps({"status": "success", "data": result}))
        except Exception as e:
            self.set_status(500)
            self.finish(json.dumps({"status": "error", "message": str(e)}))
```

### Frontend Changes

#### Phase 3: Subgroup Analysis UI
**File**: `src/api.ts`

Add API function:

```typescript
export interface ISubgroupAnalysisResult {
  subgroups: Record<string, IMetaAnalysisResult>;
  overall: IMetaAnalysisResult;
  subgroup_variable: string;
  n_subgroups: number;
}

export async function performSubgroupAnalysis(
  paperIds: number[],
  subgroupVariable: string,
  outcomeName?: string
): Promise<ISubgroupAnalysisResult> {
  const response = await requestAPI<IAPIResponse<ISubgroupAnalysisResult>>(
    'subgroup-analysis',
    {
      method: 'POST',
      body: JSON.stringify({
        paper_ids: paperIds,
        subgroup_variable: subgroupVariable,
        outcome_name: outcomeName
      })
    }
  );

  if (response.status === 'error') {
    throw new Error(response.message || 'Subgroup analysis failed');
  }

  if (!response.data) {
    throw new Error('No subgroup analysis data returned');
  }

  return response.data;
}
```

**File**: `src/widgets/SynthesisWorkbench.tsx`

Add subgroup analysis functionality:

```typescript
const [subgroupVariable, setSubgroupVariable] = useState<string>('');
const [subgroupResult, setSubgroupResult] = useState<ISubgroupAnalysisResult | null>(null);

const handleRunSubgroupAnalysis = async () => {
  if (!subgroupVariable) {
    showErrorMessage('Subgroup Analysis', 'Please select a subgroup variable');
    return;
  }
  
  setIsLoading(true);
  try {
    const result = await performSubgroupAnalysis(paperIds, subgroupVariable);
    setSubgroupResult(result);
    setActiveTab('subgroups');
  } catch (err) {
    showErrorMessage('Subgroup Analysis Error', err instanceof Error ? err.message : 'Unknown error');
  } finally {
    setIsLoading(false);
  }
};

// Add to UI:
<div className="jp-jupyterlab-research-assistant-wwc-copilot-synthesis-actions">
  {/* ... existing buttons ... */}
  <select
    value={subgroupVariable}
    onChange={(e) => setSubgroupVariable(e.target.value)}
    className="jp-jupyterlab-research-assistant-wwc-copilot-select"
  >
    <option value="">Select Subgroup Variable...</option>
    <option value="age_group">Age Group</option>
    <option value="intervention_type">Intervention Type</option>
    <option value="learning_domain">Learning Domain</option>
  </select>
  <button
    onClick={handleRunSubgroupAnalysis}
    disabled={isLoading || !subgroupVariable}
    className="jp-jupyterlab-research-assistant-wwc-copilot-button"
  >
    Run Subgroup Analysis
  </button>
</div>
```

**File**: `src/widgets/SubgroupAnalysisView.tsx` (NEW)

Create component to display subgroup results:

```typescript
import React from 'react';
import { ISubgroupAnalysisResult } from '../api';
import { MetaAnalysisView } from './MetaAnalysisView';

interface SubgroupAnalysisViewProps {
  result: ISubgroupAnalysisResult;
}

export const SubgroupAnalysisView: React.FC<SubgroupAnalysisViewProps> = ({ result }) => {
  return (
    <div className="jp-jupyterlab-research-assistant-wwc-copilot-subgroup-analysis">
      <h3>Subgroup Analysis: {result.subgroup_variable}</h3>
      
      {/* Overall Results */}
      <div className="jp-jupyterlab-research-assistant-wwc-copilot-subgroup-overall">
        <h4>Overall Meta-Analysis (All Studies)</h4>
        <MetaAnalysisView result={result.overall} />
      </div>
      
      {/* Subgroup Results */}
      <div className="jp-jupyterlab-research-assistant-wwc-copilot-subgroup-results">
        <h4>Results by Subgroup</h4>
        {Object.entries(result.subgroups).map(([subgroupName, subgroupResult]) => (
          <div key={subgroupName} className="jp-jupyterlab-research-assistant-wwc-copilot-subgroup-item">
            <h5>{subgroupName} (n={subgroupResult.n_studies})</h5>
            <MetaAnalysisView result={subgroupResult} />
          </div>
        ))}
      </div>
    </div>
  );
};
```

---

## Publication Bias Assessment

### Overview
Detect publication bias using funnel plots and Egger's test.

### Backend Changes

#### Phase 1: Funnel Plot and Egger's Test
**File**: `jupyterlab_research_assistant_wwc_copilot/services/meta_analyzer.py`

Add methods:

```python
def perform_eggers_test(
    self,
    effect_sizes: np.ndarray,
    std_errors: np.ndarray
) -> Dict:
    """
    Perform Egger's test for publication bias.
    
    Args:
        effect_sizes: Array of effect sizes
        std_errors: Array of standard errors
    
    Returns:
        Dictionary with:
            - intercept: Regression intercept
            - intercept_se: Standard error of intercept
            - intercept_pvalue: P-value for test of intercept = 0
            - interpretation: String interpretation
    """
    # Egger's test: regress effect size on precision (1/SE)
    precision = 1.0 / std_errors
    X = np.column_stack([np.ones(len(effect_sizes)), precision])
    
    # Weighted least squares
    weights = 1.0 / (std_errors ** 2)
    from scipy import linalg
    
    # Solve weighted least squares
    XW = X * weights[:, np.newaxis]
    XWX = XW.T @ X
    XWy = XW.T @ effect_sizes
    
    try:
        beta = linalg.solve(XWX, XWy)
        residuals = effect_sizes - X @ beta
        mse = np.sum(weights * residuals ** 2) / (len(effect_sizes) - 2)
        var_beta = mse * linalg.inv(XWX)
        
        intercept = beta[0]
        intercept_se = np.sqrt(var_beta[0, 0])
        intercept_t = intercept / intercept_se
        intercept_pvalue = 2 * (1 - stats.t.cdf(abs(intercept_t), len(effect_sizes) - 2))
        
        if intercept_pvalue < 0.05:
            interpretation = "Evidence of publication bias (p < 0.05)"
        else:
            interpretation = "No significant evidence of publication bias (p >= 0.05)"
        
        return {
            "intercept": float(intercept),
            "intercept_se": float(intercept_se),
            "intercept_pvalue": float(intercept_pvalue),
            "interpretation": interpretation
        }
    except Exception as e:
        return {
            "intercept": None,
            "intercept_se": None,
            "intercept_pvalue": None,
            "interpretation": f"Egger's test failed: {str(e)}"
        }
```

**File**: `jupyterlab_research_assistant_wwc_copilot/services/visualizer.py`

Add funnel plot method:

```python
def create_funnel_plot(
    self,
    effect_sizes: List[float],
    std_errors: List[float],
    labels: List[str],
    title: str = "Funnel Plot",
    figsize: tuple = (8, 8),
    dpi: int = 100
) -> str:
    """
    Generate a funnel plot for publication bias assessment.
    
    Args:
        effect_sizes: List of effect sizes
        std_errors: List of standard errors
        labels: List of study labels
        title: Plot title
        figsize: Figure size
        dpi: Resolution
    
    Returns:
        Base64-encoded PNG image string
    """
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    
    # Plot effect sizes vs precision (1/SE)
    precision = [1.0 / se for se in std_errors]
    
    ax.scatter(effect_sizes, precision, alpha=0.6, s=50)
    
    # Add labels for outliers
    for i, (es, prec, label) in enumerate(zip(effect_sizes, precision, labels)):
        if abs(es) > 2 or prec > max(precision) * 0.8:
            ax.annotate(label[:20], (es, prec), fontsize=8, alpha=0.7)
    
    ax.set_xlabel('Effect Size', fontsize=11)
    ax.set_ylabel('Precision (1/SE)', fontsize=11)
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.axvline(x=0, color='black', linestyle='--', linewidth=1, alpha=0.5)
    
    plt.tight_layout()
    
    # Convert to base64
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=dpi)
    plt.close(fig)
    buf.seek(0)
    
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    
    return image_base64
```

#### Phase 2: Bias Assessment Endpoint
**File**: `jupyterlab_research_assistant_wwc_copilot/routes.py`

Add handler:

```python
class BiasAssessmentHandler(APIHandler):
    """Handler for publication bias assessment."""
    
    @tornado.web.authenticated
    def post(self):
        """Assess publication bias."""
        try:
            data = self.get_json_body()
            paper_ids = data.get("paper_ids", [])
            outcome_name = data.get("outcome_name")
            
            # Fetch papers and extract effect sizes
            with DatabaseManager() as db:
                studies = []
                for paper_id in paper_ids:
                    paper = db.get_paper_by_id(paper_id)
                    if not paper:
                        continue
                    
                    effect_sizes = paper.get("study_metadata", {}).get("effect_sizes", {})
                    if outcome_name:
                        outcome_data = effect_sizes.get(outcome_name)
                        if outcome_data:
                            studies.append({
                                "paper_id": paper["id"],
                                "study_label": paper["title"],
                                "effect_size": outcome_data.get("d", 0.0),
                                "std_error": outcome_data.get("se", 0.1)
                            })
                
                if len(studies) < 3:  # Need at least 3 for meaningful test
                    self.set_status(400)
                    self.finish(json.dumps({
                        "status": "error",
                        "message": "At least 3 studies required for bias assessment"
                    }))
                    return
                
                # Extract arrays
                effect_sizes = np.array([s["effect_size"] for s in studies])
                std_errors = np.array([s["std_error"] for s in studies])
                labels = [s["study_label"] for s in studies]
                
                # Perform Egger's test
                analyzer = MetaAnalyzer()
                eggers_result = analyzer.perform_eggers_test(effect_sizes, std_errors)
                
                # Generate funnel plot
                visualizer = Visualizer()
                funnel_plot = visualizer.create_funnel_plot(
                    effect_sizes.tolist(),
                    std_errors.tolist(),
                    labels
                )
                
                result = {
                    "eggers_test": eggers_result,
                    "funnel_plot": funnel_plot,
                    "n_studies": len(studies)
                }
                
                self.finish(json.dumps({"status": "success", "data": result}))
        except Exception as e:
            self.set_status(500)
            self.finish(json.dumps({"status": "error", "message": str(e)}))
```

### Frontend Changes

#### Phase 3: Bias Assessment UI
**File**: `src/api.ts`

Add types and function:

```typescript
export interface IBiasAssessmentResult {
  eggers_test: {
    intercept: number | null;
    intercept_se: number | null;
    intercept_pvalue: number | null;
    interpretation: string;
  };
  funnel_plot: string;
  n_studies: number;
}

export async function assessPublicationBias(
  paperIds: number[],
  outcomeName?: string
): Promise<IBiasAssessmentResult> {
  const response = await requestAPI<IAPIResponse<IBiasAssessmentResult>>(
    'bias-assessment',
    {
      method: 'POST',
      body: JSON.stringify({
        paper_ids: paperIds,
        outcome_name: outcomeName
      })
    }
  );

  if (response.status === 'error') {
    throw new Error(response.message || 'Bias assessment failed');
  }

  if (!response.data) {
    throw new Error('No bias assessment data returned');
  }

  return response.data;
}
```

**File**: `src/widgets/BiasAssessmentView.tsx` (NEW)

Create component:

```typescript
import React from 'react';
import { IBiasAssessmentResult } from '../api';

interface BiasAssessmentViewProps {
  result: IBiasAssessmentResult;
}

export const BiasAssessmentView: React.FC<BiasAssessmentViewProps> = ({ result }) => {
  return (
    <div className="jp-jupyterlab-research-assistant-wwc-copilot-bias-assessment">
      <h3>Publication Bias Assessment</h3>
      
      {/* Egger's Test Results */}
      <div className="jp-jupyterlab-research-assistant-wwc-copilot-eggers-test">
        <h4>Egger's Test</h4>
        {result.eggers_test.intercept_pvalue !== null ? (
          <div>
            <p><strong>Intercept:</strong> {result.eggers_test.intercept?.toFixed(4)}</p>
            <p><strong>P-value:</strong> {result.eggers_test.intercept_pvalue.toFixed(4)}</p>
            <p><strong>Interpretation:</strong> {result.eggers_test.interpretation}</p>
          </div>
        ) : (
          <p>{result.eggers_test.interpretation}</p>
        )}
      </div>
      
      {/* Funnel Plot */}
      {result.funnel_plot && (
        <div className="jp-jupyterlab-research-assistant-wwc-copilot-funnel-plot">
          <h4>Funnel Plot</h4>
          <img
            src={`data:image/png;base64,${result.funnel_plot}`}
            alt="Funnel Plot"
            style={{ maxWidth: '100%', height: 'auto' }}
          />
        </div>
      )}
    </div>
  );
};
```

---

## Advanced Conflict Detection

### Overview
Improve conflict detection by using AI extraction to identify key findings more accurately.

### Backend Changes

#### Phase 1: AI-Based Finding Extraction
**File**: `jupyterlab_research_assistant_wwc_copilot/services/conflict_detector.py`

Enhance `extract_key_findings()` method:

```python
def extract_key_findings(
    self,
    paper_text: str,
    max_findings: int = 5,
    use_ai: bool = True
) -> List[str]:
    """
    Extract key findings from paper text using AI extraction.
    
    Args:
        paper_text: Full text of the paper
        max_findings: Maximum number of findings to extract
        use_ai: Whether to use AI extraction (if available)
    
    Returns:
        List of finding statements
    """
    if use_ai and self.ai_extractor:
        # Use AI extraction service to identify key findings
        schema = {
            "type": "object",
            "properties": {
                "key_findings": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of key findings or conclusions from the study"
                }
            },
            "required": ["key_findings"]
        }
        
        try:
            result = self.ai_extractor.extract_metadata(paper_text, schema)
            findings = result.get("key_findings", [])
            return findings[:max_findings]
        except Exception as e:
            logger.warning(f"AI extraction failed, falling back to keyword method: {str(e)}")
    
    # Fallback to keyword-based extraction
    findings = []
    keywords = ["significant", "found that", "results show", "conclusion", "demonstrated"]
    sentences = paper_text.split('.')
    
    for sentence in sentences:
        if any(kw in sentence.lower() for kw in keywords) and len(sentence.strip()) > 20:
            findings.append(sentence.strip())
            if len(findings) >= max_findings:
                break
    
    return findings
```

**File**: `jupyterlab_research_assistant_wwc_copilot/services/conflict_detector.py`

Update `__init__` to accept AI extractor:

```python
def __init__(self, model_name: str = "cross-encoder/nli-deberta-v3-base", ai_extractor=None):
    """
    Initialize NLI pipeline.
    
    Args:
        model_name: Hugging Face model identifier for NLI model
        ai_extractor: Optional AI extractor service for finding extraction
    """
    self.model_name = model_name
    self.nli_pipeline = None
    self.ai_extractor = ai_extractor  # Add AI extractor
    
    # ... rest of initialization
```

### Frontend Changes

#### Phase 2: Finding Preview UI
**File**: `src/widgets/ConflictView.tsx`

Add finding preview before conflict detection:

```typescript
interface ConflictViewProps {
  result: IConflictDetectionResult;
  findings?: Record<number, string[]>; // Optional: extracted findings by paper ID
}

export const ConflictView: React.FC<ConflictViewProps> = ({ result, findings }) => {
  return (
    <div className="jp-jupyterlab-research-assistant-wwc-copilot-conflicts">
      <h3>Conflict Detection Results</h3>
      
      {/* Findings Preview */}
      {findings && Object.keys(findings).length > 0 && (
        <div className="jp-jupyterlab-research-assistant-wwc-copilot-findings-preview">
          <h4>Extracted Key Findings</h4>
          {Object.entries(findings).map(([paperId, paperFindings]) => (
            <div key={paperId} className="jp-jupyterlab-research-assistant-wwc-copilot-finding-item">
              <strong>Paper {paperId}:</strong>
              <ul>
                {paperFindings.map((finding, idx) => (
                  <li key={idx}>{finding}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}
      
      {/* Rest of conflict display */}
      {/* ... */}
    </div>
  );
};
```

---

## Sensitivity Analysis

### Overview
Perform leave-one-out analysis and influence diagnostics to identify studies that heavily influence results.

### Backend Changes

#### Phase 1: Sensitivity Analysis Service
**File**: `jupyterlab_research_assistant_wwc_copilot/services/meta_analyzer.py`

Add methods:

```python
def perform_sensitivity_analysis(
    self,
    studies: List[Dict]
) -> Dict:
    """
    Perform sensitivity analysis (leave-one-out and influence diagnostics).
    
    Args:
        studies: List of study dictionaries
    
    Returns:
        Dictionary with:
            - leave_one_out: List of results with each study removed
            - influence_diagnostics: Cook's distance and other influence measures
    """
    # Perform overall meta-analysis
    overall_result = self.perform_random_effects_meta_analysis(studies)
    overall_effect = overall_result["pooled_effect"]
    
    # Leave-one-out analysis
    leave_one_out_results = []
    for i in range(len(studies)):
        studies_without_i = [s for j, s in enumerate(studies) if j != i]
        if len(studies_without_i) >= 2:
            result = self.perform_random_effects_meta_analysis(studies_without_i)
            leave_one_out_results.append({
                "removed_study": studies[i].get("study_label", f"Study {i+1}"),
                "removed_paper_id": studies[i].get("paper_id"),
                "pooled_effect": result["pooled_effect"],
                "ci_lower": result["ci_lower"],
                "ci_upper": result["ci_upper"],
                "difference_from_overall": result["pooled_effect"] - overall_effect
            })
    
    # Influence diagnostics (simplified Cook's distance)
    effect_sizes = np.array([s["effect_size"] for s in studies])
    std_errors = np.array([s["std_error"] for s in studies])
    weights = 1.0 / (std_errors ** 2 + overall_result["tau_squared"])
    weights = weights / weights.sum()
    
    # Calculate influence (how much each study affects overall result)
    influence_scores = []
    for i, study in enumerate(studies):
        # Simplified influence: weight * absolute deviation from mean
        mean_effect = np.average(effect_sizes, weights=weights)
        influence = weights[i] * abs(effect_sizes[i] - mean_effect)
        influence_scores.append({
            "study_label": study.get("study_label", f"Study {i+1}"),
            "paper_id": study.get("paper_id"),
            "influence_score": float(influence),
            "weight": float(weights[i]),
            "effect_size": float(effect_sizes[i])
        })
    
    # Sort by influence
    influence_scores.sort(key=lambda x: x["influence_score"], reverse=True)
    
    return {
        "overall_effect": overall_effect,
        "leave_one_out": leave_one_out_results,
        "influence_diagnostics": influence_scores,
        "n_studies": len(studies)
    }
```

#### Phase 2: Sensitivity Analysis Endpoint
**File**: `jupyterlab_research_assistant_wwc_copilot/routes.py`

Add handler:

```python
class SensitivityAnalysisHandler(APIHandler):
    """Handler for sensitivity analysis."""
    
    @tornado.web.authenticated
    def post(self):
        """Perform sensitivity analysis."""
        try:
            data = self.get_json_body()
            paper_ids = data.get("paper_ids", [])
            outcome_name = data.get("outcome_name")
            
            # Fetch papers (similar to meta-analysis handler)
            with DatabaseManager() as db:
                studies = []
                for paper_id in paper_ids:
                    paper = db.get_paper_by_id(paper_id)
                    if not paper:
                        continue
                    
                    effect_sizes = paper.get("study_metadata", {}).get("effect_sizes", {})
                    if outcome_name:
                        outcome_data = effect_sizes.get(outcome_name)
                        if outcome_data:
                            studies.append({
                                "paper_id": paper["id"],
                                "study_label": paper["title"],
                                "effect_size": outcome_data.get("d", 0.0),
                                "std_error": outcome_data.get("se", 0.1)
                            })
                
                if len(studies) < 3:
                    self.set_status(400)
                    self.finish(json.dumps({
                        "status": "error",
                        "message": "At least 3 studies required for sensitivity analysis"
                    }))
                    return
                
                analyzer = MetaAnalyzer()
                result = analyzer.perform_sensitivity_analysis(studies)
                
                self.finish(json.dumps({"status": "success", "data": result}))
        except Exception as e:
            self.set_status(500)
            self.finish(json.dumps({"status": "error", "message": str(e)}))
```

### Frontend Changes

#### Phase 3: Sensitivity Analysis UI
**File**: `src/api.ts`

Add types and function:

```typescript
export interface ISensitivityAnalysisResult {
  overall_effect: number;
  leave_one_out: Array<{
    removed_study: string;
    removed_paper_id?: number;
    pooled_effect: number;
    ci_lower: number;
    ci_upper: number;
    difference_from_overall: number;
  }>;
  influence_diagnostics: Array<{
    study_label: string;
    paper_id?: number;
    influence_score: number;
    weight: number;
    effect_size: number;
  }>;
  n_studies: number;
}

export async function performSensitivityAnalysis(
  paperIds: number[],
  outcomeName?: string
): Promise<ISensitivityAnalysisResult> {
  const response = await requestAPI<IAPIResponse<ISensitivityAnalysisResult>>(
    'sensitivity-analysis',
    {
      method: 'POST',
      body: JSON.stringify({
        paper_ids: paperIds,
        outcome_name: outcomeName
      })
    }
  );

  if (response.status === 'error') {
    throw new Error(response.message || 'Sensitivity analysis failed');
  }

  if (!response.data) {
    throw new Error('No sensitivity analysis data returned');
  }

  return response.data;
}
```

**File**: `src/widgets/SensitivityAnalysisView.tsx` (NEW)

Create component:

```typescript
import React from 'react';
import { ISensitivityAnalysisResult } from '../api';

interface SensitivityAnalysisViewProps {
  result: ISensitivityAnalysisResult;
}

export const SensitivityAnalysisView: React.FC<SensitivityAnalysisViewProps> = ({ result }) => {
  return (
    <div className="jp-jupyterlab-research-assistant-wwc-copilot-sensitivity-analysis">
      <h3>Sensitivity Analysis</h3>
      
      {/* Overall Effect */}
      <div className="jp-jupyterlab-research-assistant-wwc-copilot-sensitivity-overall">
        <h4>Overall Effect (All Studies)</h4>
        <p>Pooled Effect: {result.overall_effect.toFixed(3)}</p>
      </div>
      
      {/* Leave-One-Out Results */}
      <div className="jp-jupyterlab-research-assistant-wwc-copilot-sensitivity-loo">
        <h4>Leave-One-Out Analysis</h4>
        <p>Effect size when each study is removed:</p>
        <table className="jp-jupyterlab-research-assistant-wwc-copilot-table">
          <thead>
            <tr>
              <th>Removed Study</th>
              <th>Pooled Effect</th>
              <th>95% CI</th>
              <th>Difference</th>
            </tr>
          </thead>
          <tbody>
            {result.leave_one_out.map((loo, idx) => (
              <tr key={idx}>
                <td>{loo.removed_study}</td>
                <td>{loo.pooled_effect.toFixed(3)}</td>
                <td>[{loo.ci_lower.toFixed(3)}, {loo.ci_upper.toFixed(3)}]</td>
                <td style={{ color: Math.abs(loo.difference_from_overall) > 0.2 ? '#f44336' : 'inherit' }}>
                  {loo.difference_from_overall > 0 ? '+' : ''}{loo.difference_from_overall.toFixed(3)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      {/* Influence Diagnostics */}
      <div className="jp-jupyterlab-research-assistant-wwc-copilot-sensitivity-influence">
        <h4>Influence Diagnostics</h4>
        <p>Studies ranked by influence on overall result:</p>
        <table className="jp-jupyterlab-research-assistant-wwc-copilot-table">
          <thead>
            <tr>
              <th>Study</th>
              <th>Influence Score</th>
              <th>Weight</th>
              <th>Effect Size</th>
            </tr>
          </thead>
          <tbody>
            {result.influence_diagnostics.map((diag, idx) => (
              <tr key={idx}>
                <td>{diag.study_label}</td>
                <td>{diag.influence_score.toFixed(4)}</td>
                <td>{(diag.weight * 100).toFixed(1)}%</td>
                <td>{diag.effect_size.toFixed(3)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
```

---

## Testing Checklist

For each enhancement, test:
- [ ] Backend endpoints respond correctly
- [ ] Frontend components render properly
- [ ] Error handling works (missing data, network errors)
- [ ] UI is responsive and accessible
- [ ] Results are accurate and match expected calculations
- [ ] Integration with existing features works
- [ ] Performance is acceptable with large datasets

---

## Implementation Order Recommendation

1. **Subgroup Analysis** (High priority, common use case)
2. **Publication Bias Assessment** (High priority, standard practice)
3. **Sensitivity Analysis** (Medium priority, useful robustness check)
4. **Enhanced WWC UI** (Medium priority, UX improvement)
5. **Advanced Conflict Detection** (Lower priority, current implementation works)

---

## Notes

- Each enhancement can be implemented independently
- Consider user feedback to prioritize
- Some enhancements may require additional dependencies (e.g., scipy for Egger's test)
- All enhancements should maintain backward compatibility with existing features

