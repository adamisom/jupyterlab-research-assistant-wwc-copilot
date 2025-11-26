import React, { useState, useEffect, useCallback, useRef } from 'react';
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
  const isRunningRef = useRef(false); // Prevent concurrent assessment calls

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
    // Prevent concurrent calls
    if (isRunningRef.current) {
      return;
    }
    isRunningRef.current = true;
    try {
      const result = await executeAssessment(paperId, judgments);
      if (result) {
        setAssessment(result);
        saveProgress();
      }
    } finally {
      isRunningRef.current = false;
    }
  }, [paperId, judgments, executeAssessment]);

  // Only auto-run assessment when moving to review step (not on every judgment change)
  useEffect(() => {
    if (currentStep === 'review' && !assessment && !isAssessmentLoading) {
      // Only run if we don't already have an assessment and not currently loading
      runAssessment();
    }
    // Intentionally exclude runAssessment from deps to prevent infinite loops
  }, [currentStep]);

  // Handle errors - only show once per error
  const [lastError, setLastError] = useState<Error | null>(null);
  useEffect(() => {
    if (assessmentError && assessmentError !== lastError) {
      setLastError(assessmentError);
      showError(
        'WWC Assessment Error',
        assessmentError.message || 'Failed to fetch assessment',
        assessmentError
      );
    }
  }, [assessmentError, lastError]);

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

  const getRatingColorClass = (rating: string) => {
    if (rating.includes('Without Reservations')) {
      return 'jp-type-meets-standards';
    }
    if (rating.includes('With Reservations')) {
      return 'jp-type-meets-with-reservations';
    }
    return 'jp-type-does-not-meet';
  };

  return (
    <div className="jp-WWCExtension-wwc">
      <div className="jp-WWCExtension-wwc-header">
        <h2>WWC Co-Pilot: {paperTitle}</h2>
        {onClose && (
          <button onClick={onClose} className="jp-WWCExtension-close">
            ×
          </button>
        )}
      </div>

      {/* Info Boxes - Always show info, conditionally show warning */}
      <div className="jp-WWCExtension-wwc-info-container">
        {/* Always-visible informational box */}
        <div className="jp-WWCExtension-wwc-info-box">
          <div className="jp-WWCExtension-wwc-info-content">
            <strong>ℹ️ About WWC Assessment</strong>
            <p>
              WWC assessment evaluates studies based on randomization
              documentation, attrition rates, baseline equivalence, and
              statistical adjustments. Complete the wizard steps to get your
              assessment rating.
            </p>
          </div>
        </div>

        {/* Warning box - Show if assessment found missing data or if assessment failed */}
        {(assessmentError ||
          (assessment &&
            (assessment.overall_attrition === undefined ||
              assessment.rating_justification.some(
                msg =>
                  msg.includes('incomplete') ||
                  msg.includes('Insufficient data')
              )))) && (
          <div className="jp-WWCExtension-wwc-warning-box">
            <div className="jp-WWCExtension-wwc-warning-content">
              <strong>⚠️ Missing Required Data</strong>
              <p>
                Attrition data was not found in this paper. Without sample sizes
                and attrition rates, the assessment will default to "Does Not
                Meet WWC Standards."
              </p>
              <p>
                To complete the assessment, ensure the paper has{' '}
                <code>study_metadata</code> with sample sizes and attrition
                data. This can be added via AI extraction during PDF upload (if
                configured) or manually.
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Progress Indicator */}
      <div className="jp-WWCExtension-wwc-progress">
        <div className="jp-WWCExtension-wwc-progress-bar">
          <div
            className="jp-WWCExtension-wwc-progress-fill"
            style={{ width: `${progress}%` }}
          />
        </div>
        <div className="jp-WWCExtension-wwc-steps">
          {steps.map((step, idx) => (
            <button
              key={step}
              className={`jp-WWCExtension-step ${
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
        <div className="jp-WWCExtension-loading">Running assessment...</div>
      )}

      {/* Step Content */}
      <div className="jp-WWCExtension-wwc-content">
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
            getRatingColorClass={getRatingColorClass}
          />
        )}
      </div>

      {/* Navigation Buttons */}
      <div className="jp-WWCExtension-wwc-navigation">
        <button
          onClick={handlePrevious}
          disabled={currentStep === steps[0]}
          className="jp-WWCExtension-button"
        >
          Previous
        </button>
        {currentStep !== steps[steps.length - 1] ? (
          <button onClick={handleNext} className="jp-WWCExtension-button">
            Next
          </button>
        ) : (
          <button
            onClick={runAssessment}
            disabled={isAssessmentLoading}
            className="jp-WWCExtension-button"
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
  <div className="jp-WWCExtension-wwc-step-content">
    <h3>Step 1: Randomization</h3>
    <p>Was randomization properly documented in the study?</p>
    <select
      value={
        randomizationDocumented === undefined
          ? ''
          : String(randomizationDocumented)
      }
      onChange={e => onChange(e.target.value === 'true')}
      className="jp-WWCExtension-select"
    >
      <option value="">Not specified</option>
      <option value="true">Yes</option>
      <option value="false">No</option>
    </select>
    <p className="jp-WWCExtension-wwc-help">
      Randomization must be clearly described in the study methodology.
    </p>
  </div>
);

const AttritionStep: React.FC<{
  boundary: string;
  onChange: (value: 'cautious' | 'optimistic') => void;
  assessment: IWWCAssessment | null;
}> = ({ boundary, onChange, assessment }) => (
  <div className="jp-WWCExtension-wwc-step-content">
    <h3>Step 2: Attrition</h3>
    <div className="jp-WWCExtension-wwc-field">
      <label>Attrition Boundary:</label>
      <select
        value={boundary}
        onChange={e => onChange(e.target.value as 'cautious' | 'optimistic')}
        className="jp-WWCExtension-select"
      >
        <option value="cautious">Cautious (default)</option>
        <option value="optimistic">Optimistic</option>
      </select>
      <p className="jp-WWCExtension-wwc-help">
        Choose based on whether the intervention could affect who stays in the
        study.
      </p>
    </div>
    {assessment && (
      <div className="jp-WWCExtension-wwc-section">
        <h4>Attrition Results</h4>
        {assessment.overall_attrition !== null &&
          assessment.overall_attrition !== undefined && (
            <p>Overall: {formatPercent(assessment.overall_attrition, 1)}</p>
          )}
        {assessment.differential_attrition !== null &&
          assessment.differential_attrition !== undefined && (
            <p>
              Differential:{' '}
              {formatPercent(assessment.differential_attrition, 1)}
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
  <div className="jp-WWCExtension-wwc-step-content">
    <h3>Step 3: Baseline Equivalence</h3>
    {assessment?.baseline_effect_size !== null &&
    assessment?.baseline_effect_size !== undefined ? (
      <div className="jp-WWCExtension-wwc-section">
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
  <div className="jp-WWCExtension-wwc-step-content">
    <h3>Step 4: Statistical Adjustment</h3>
    <p>Was a valid statistical adjustment used?</p>
    <select
      value={adjustmentValid === undefined ? '' : String(adjustmentValid)}
      onChange={e => onChange(e.target.value === 'true')}
      className="jp-WWCExtension-select"
    >
      <option value="">Not applicable</option>
      <option value="true">Yes</option>
      <option value="false">No</option>
    </select>
    <p className="jp-WWCExtension-wwc-help">
      Required for studies with high attrition or baseline differences.
    </p>
  </div>
);

const ReviewStep: React.FC<{
  assessment: IWWCAssessment | null;
  judgments: IWWCAssessmentRequest['judgments'];
  onRunAssessment: () => void;
  isLoading: boolean;
  getRatingColorClass: (rating: string) => string;
}> = ({
  assessment,
  judgments,
  onRunAssessment,
  isLoading,
  getRatingColorClass
}) => (
  <div className="jp-WWCExtension-wwc-step-content">
    <h3>Step 5: Review & Finalize</h3>
    <div className="jp-WWCExtension-wwc-judgments">
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
      <div className="jp-WWCExtension-wwc-results">
        <h4>Final Rating</h4>
        <div
          className={`jp-WWCExtension-wwc-rating ${getRatingColorClass(assessment.final_rating)}`}
        >
          <strong>Final Rating: {assessment.final_rating}</strong>
        </div>
        <div className="jp-WWCExtension-wwc-justification">
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
