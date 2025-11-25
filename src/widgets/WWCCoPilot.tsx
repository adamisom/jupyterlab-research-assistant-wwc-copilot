import React, { useState, useEffect, useCallback } from 'react';
import {
  runWWCAssessment,
  IWWCAssessment,
  IWWCAssessmentRequest
} from '../api';
import { showError } from '../utils/notifications';
import { useAsyncOperation } from '../utils/hooks';
import { formatPercent, formatNumber } from '../utils/format';

interface WWCCoPilotProps {
  paperId: number;
  paperTitle: string;
  onClose?: () => void;
}

type WizardStep =
  | 'randomization'
  | 'attrition'
  | 'baseline'
  | 'adjustment'
  | 'review';

export const WWCCoPilot: React.FC<WWCCoPilotProps> = ({
  paperId,
  paperTitle,
  onClose
}) => {
  const [currentStep, setCurrentStep] = useState<WizardStep>('randomization');
  const [assessment, setAssessment] = useState<IWWCAssessment | null>(null);
  const [judgments, setJudgments] = useState<
    IWWCAssessmentRequest['judgments']
  >({
    chosen_attrition_boundary: 'cautious',
    adjustment_strategy_is_valid: undefined,
    randomization_documented: undefined
  });

  const steps: WizardStep[] = [
    'randomization',
    'attrition',
    'baseline',
    'adjustment',
    'review'
  ];
  const stepLabels = {
    randomization: 'Randomization',
    attrition: 'Attrition',
    baseline: 'Baseline Equivalence',
    adjustment: 'Statistical Adjustment',
    review: 'Review & Finalize'
  };

  const getStepIndex = (step: WizardStep): number => steps.indexOf(step);
  const progress = ((getStepIndex(currentStep) + 1) / steps.length) * 100;

  // Load saved assessment from localStorage
  useEffect(() => {
    const saved = localStorage.getItem(`wwc-assessment-${paperId}`);
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        if (parsed.judgments) {
          setJudgments(parsed.judgments);
        }
        if (parsed.currentStep) {
          setCurrentStep(parsed.currentStep);
        }
      } catch (e) {
        console.error('Failed to load saved assessment:', e);
      }
    }
  }, [paperId]);

  const saveProgress = () => {
    localStorage.setItem(
      `wwc-assessment-${paperId}`,
      JSON.stringify({
        judgments,
        currentStep
      })
    );
  };

  const runAssessmentWithRequest = async (
    paperId: number,
    judgments: IWWCAssessmentRequest['judgments']
  ): Promise<IWWCAssessment> => {
    const request: IWWCAssessmentRequest = {
      paper_id: paperId,
      judgments
    };
    return await runWWCAssessment(request);
  };

  const [isAssessmentLoading, executeAssessment, assessmentError] =
    useAsyncOperation(runAssessmentWithRequest);

  const runAssessment = useCallback(async () => {
    const result = await executeAssessment(paperId, judgments);
    if (result) {
      setAssessment(result);
      saveProgress();
    }
  }, [paperId, judgments, executeAssessment]);

  // Auto-run assessment when judgments change (except on initial load)
  useEffect(() => {
    if (currentStep !== 'randomization') {
      runAssessment();
    }
  }, [judgments, currentStep, runAssessment]);

  // Handle errors
  useEffect(() => {
    if (assessmentError) {
      showError(
        'WWC Assessment Error',
        assessmentError.message,
        assessmentError
      );
    }
  }, [assessmentError]);

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

  const getRatingColor = (rating: string) => {
    if (rating.includes('Without Reservations')) {
      return '#4caf50';
    } // Green
    if (rating.includes('With Reservations')) {
      return '#ff9800';
    } // Orange
    return '#f44336'; // Red
  };

  return (
    <div className="jp-jupyterlab-research-assistant-wwc-copilot-wwc">
      <div className="jp-jupyterlab-research-assistant-wwc-copilot-wwc-header">
        <h2>WWC Co-Pilot: {paperTitle}</h2>
        {onClose && (
          <button
            onClick={onClose}
            className="jp-jupyterlab-research-assistant-wwc-copilot-close"
          >
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

      {isAssessmentLoading && (
        <div className="jp-jupyterlab-research-assistant-wwc-copilot-loading">
          Running assessment...
        </div>
      )}

      {/* Step Content */}
      <div className="jp-jupyterlab-research-assistant-wwc-copilot-wwc-content">
        {currentStep === 'randomization' && (
          <RandomizationStep
            randomizationDocumented={judgments.randomization_documented}
            onChange={value => {
              setJudgments({ ...judgments, randomization_documented: value });
              saveProgress();
            }}
          />
        )}
        {currentStep === 'attrition' && (
          <AttritionStep
            boundary={judgments.chosen_attrition_boundary || 'cautious'}
            onChange={value => {
              setJudgments({ ...judgments, chosen_attrition_boundary: value });
              saveProgress();
            }}
            assessment={assessment}
          />
        )}
        {currentStep === 'baseline' && <BaselineStep assessment={assessment} />}
        {currentStep === 'adjustment' && (
          <AdjustmentStep
            adjustmentValid={judgments.adjustment_strategy_is_valid}
            onChange={value => {
              setJudgments({
                ...judgments,
                adjustment_strategy_is_valid: value
              });
              saveProgress();
            }}
          />
        )}
        {currentStep === 'review' && (
          <ReviewStep
            assessment={assessment}
            judgments={judgments}
            onRunAssessment={runAssessment}
            isLoading={isAssessmentLoading}
            getRatingColor={getRatingColor}
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
            disabled={isAssessmentLoading}
            className="jp-jupyterlab-research-assistant-wwc-copilot-button"
          >
            {isAssessmentLoading ? 'Running...' : 'Run Assessment'}
          </button>
        )}
      </div>
    </div>
  );
};

// Individual step components
const RandomizationStep: React.FC<{
  randomizationDocumented?: boolean;
  onChange: (value: boolean) => void;
}> = ({ randomizationDocumented, onChange }) => (
  <div className="jp-jupyterlab-research-assistant-wwc-copilot-wwc-step-content">
    <h3>Step 1: Randomization</h3>
    <p>Was randomization properly documented in the study?</p>
    <select
      value={
        randomizationDocumented === undefined
          ? ''
          : String(randomizationDocumented)
      }
      onChange={e => onChange(e.target.value === 'true')}
      className="jp-jupyterlab-research-assistant-wwc-copilot-select"
    >
      <option value="">Not specified</option>
      <option value="true">Yes</option>
      <option value="false">No</option>
    </select>
    <p className="jp-jupyterlab-research-assistant-wwc-copilot-wwc-help">
      Randomization must be clearly described in the study methodology.
    </p>
  </div>
);

const AttritionStep: React.FC<{
  boundary: string;
  onChange: (value: 'cautious' | 'optimistic') => void;
  assessment: IWWCAssessment | null;
}> = ({ boundary, onChange, assessment }) => (
  <div className="jp-jupyterlab-research-assistant-wwc-copilot-wwc-step-content">
    <h3>Step 2: Attrition</h3>
    <div className="jp-jupyterlab-research-assistant-wwc-copilot-wwc-field">
      <label>Attrition Boundary:</label>
      <select
        value={boundary}
        onChange={e => onChange(e.target.value as 'cautious' | 'optimistic')}
        className="jp-jupyterlab-research-assistant-wwc-copilot-select"
      >
        <option value="cautious">Cautious (default)</option>
        <option value="optimistic">Optimistic</option>
      </select>
      <p className="jp-jupyterlab-research-assistant-wwc-copilot-wwc-help">
        Choose based on whether the intervention could affect who stays in the
        study.
      </p>
    </div>
    {assessment && (
      <div className="jp-jupyterlab-research-assistant-wwc-copilot-wwc-section">
        <h4>Attrition Results</h4>
        {assessment.overall_attrition !== undefined && (
          <p>Overall: {formatPercent(assessment.overall_attrition, 1)}</p>
        )}
        {assessment.differential_attrition !== undefined && (
          <p>
            Differential: {formatPercent(assessment.differential_attrition, 1)}
          </p>
        )}
        {assessment.is_high_attrition !== undefined && (
          <p>
            Status:{' '}
            <strong>
              {assessment.is_high_attrition
                ? 'High Attrition'
                : 'Low Attrition'}
            </strong>
          </p>
        )}
      </div>
    )}
  </div>
);

const BaselineStep: React.FC<{ assessment: IWWCAssessment | null }> = ({
  assessment
}) => (
  <div className="jp-jupyterlab-research-assistant-wwc-copilot-wwc-step-content">
    <h3>Step 3: Baseline Equivalence</h3>
    {assessment?.baseline_effect_size !== undefined ? (
      <div className="jp-jupyterlab-research-assistant-wwc-copilot-wwc-section">
        <p>
          Effect Size (Cohen's d):{' '}
          {formatNumber(assessment.baseline_effect_size, 3)}
        </p>
        {assessment.baseline_equivalence_satisfied !== undefined && (
          <p>
            Status:{' '}
            <strong>
              {assessment.baseline_equivalence_satisfied
                ? 'Satisfied'
                : 'Not Satisfied'}
            </strong>
          </p>
        )}
      </div>
    ) : (
      <p>
        Baseline equivalence will be calculated after running the assessment.
      </p>
    )}
  </div>
);

const AdjustmentStep: React.FC<{
  adjustmentValid?: boolean;
  onChange: (value: boolean) => void;
}> = ({ adjustmentValid, onChange }) => (
  <div className="jp-jupyterlab-research-assistant-wwc-copilot-wwc-step-content">
    <h3>Step 4: Statistical Adjustment</h3>
    <p>Was a valid statistical adjustment used?</p>
    <select
      value={adjustmentValid === undefined ? '' : String(adjustmentValid)}
      onChange={e => onChange(e.target.value === 'true')}
      className="jp-jupyterlab-research-assistant-wwc-copilot-select"
    >
      <option value="">Not applicable</option>
      <option value="true">Yes</option>
      <option value="false">No</option>
    </select>
    <p className="jp-jupyterlab-research-assistant-wwc-copilot-wwc-help">
      Required for studies with high attrition or baseline differences.
    </p>
  </div>
);

const ReviewStep: React.FC<{
  assessment: IWWCAssessment | null;
  judgments: IWWCAssessmentRequest['judgments'];
  onRunAssessment: () => void;
  isLoading: boolean;
  getRatingColor: (rating: string) => string;
}> = ({
  assessment,
  judgments,
  onRunAssessment,
  isLoading,
  getRatingColor
}) => (
  <div className="jp-jupyterlab-research-assistant-wwc-copilot-wwc-step-content">
    <h3>Step 5: Review & Finalize</h3>
    <div className="jp-jupyterlab-research-assistant-wwc-copilot-wwc-judgments">
      <h4>Your Judgments:</h4>
      <ul>
        <li>
          Attrition Boundary:{' '}
          {judgments.chosen_attrition_boundary || 'cautious'}
        </li>
        <li>
          Randomization Documented:{' '}
          {judgments.randomization_documented?.toString() || 'Not specified'}
        </li>
        <li>
          Adjustment Valid:{' '}
          {judgments.adjustment_strategy_is_valid?.toString() ||
            'Not applicable'}
        </li>
      </ul>
    </div>
    {assessment && (
      <div className="jp-jupyterlab-research-assistant-wwc-copilot-wwc-results">
        <h4>Final Rating</h4>
        <div
          className="jp-jupyterlab-research-assistant-wwc-copilot-wwc-rating"
          style={{
            backgroundColor: getRatingColor(assessment.final_rating),
            color: 'white',
            padding: '12px',
            borderRadius: '4px',
            marginBottom: '16px'
          }}
        >
          <strong>Final Rating: {assessment.final_rating}</strong>
        </div>
        <div className="jp-jupyterlab-research-assistant-wwc-copilot-wwc-justification">
          <h4>Justification</h4>
          <ul>
            {assessment.rating_justification.map((reason, idx) => (
              <li key={idx}>{reason}</li>
            ))}
          </ul>
        </div>
      </div>
    )}
    {!assessment && (
      <p>Click "Run Assessment" to calculate the final WWC rating.</p>
    )}
  </div>
);
