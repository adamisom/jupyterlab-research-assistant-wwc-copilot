import React, { useState, useEffect } from 'react';
import {
  runWWCAssessment,
  IWWCAssessment,
  IWWCAssessmentRequest
} from '../api';
import { showErrorMessage } from '@jupyterlab/apputils';

interface IWWCCoPilotProps {
  paperId: number;
  paperTitle: string;
  onClose?: () => void;
}

export const WWCCoPilot: React.FC<IWWCCoPilotProps> = ({
  paperId,
  paperTitle,
  onClose
}) => {
  const [assessment, setAssessment] = useState<IWWCAssessment | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [judgments, setJudgments] = useState<
    IWWCAssessmentRequest['judgments']
  >({
    chosen_attrition_boundary: 'cautious',
    adjustment_strategy_is_valid: undefined,
    randomization_documented: undefined
  });

  useEffect(() => {
    runAssessment();
  }, [paperId, judgments]);

  const runAssessment = async () => {
    setIsLoading(true);
    try {
      const request: IWWCAssessmentRequest = {
        paper_id: paperId,
        judgments
      };
      const result = await runWWCAssessment(request);
      setAssessment(result);
    } catch (err) {
      showErrorMessage(
        'WWC Assessment Error',
        err instanceof Error ? err.message : 'Unknown error'
      );
    } finally {
      setIsLoading(false);
    }
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

      {isLoading && (
        <div className="jp-jupyterlab-research-assistant-wwc-copilot-loading">
          Running assessment...
        </div>
      )}

      {assessment && (
        <>
          {/* User Judgment Section */}
          <div className="jp-jupyterlab-research-assistant-wwc-copilot-wwc-judgments">
            <h3>Your Judgments</h3>

            <div className="jp-jupyterlab-research-assistant-wwc-copilot-wwc-field">
              <label>Attrition Boundary:</label>
              <select
                value={judgments.chosen_attrition_boundary || 'cautious'}
                onChange={e =>
                  setJudgments({
                    ...judgments,
                    chosen_attrition_boundary: e.target.value as
                      | 'cautious'
                      | 'optimistic'
                  })
                }
              >
                <option value="cautious">Cautious (default)</option>
                <option value="optimistic">Optimistic</option>
              </select>
              <p className="jp-jupyterlab-research-assistant-wwc-copilot-wwc-help">
                Choose based on whether the intervention could affect who stays
                in the study.
              </p>
            </div>

            <div className="jp-jupyterlab-research-assistant-wwc-copilot-wwc-field">
              <label>Randomization Documented:</label>
              <select
                value={
                  judgments.randomization_documented === undefined
                    ? ''
                    : String(judgments.randomization_documented)
                }
                onChange={e =>
                  setJudgments({
                    ...judgments,
                    randomization_documented:
                      e.target.value === ''
                        ? undefined
                        : e.target.value === 'true'
                  })
                }
              >
                <option value="">Not specified</option>
                <option value="true">Yes</option>
                <option value="false">No</option>
              </select>
            </div>

            <div className="jp-jupyterlab-research-assistant-wwc-copilot-wwc-field">
              <label>Statistical Adjustment Valid:</label>
              <select
                value={
                  judgments.adjustment_strategy_is_valid === undefined
                    ? ''
                    : String(judgments.adjustment_strategy_is_valid)
                }
                onChange={e =>
                  setJudgments({
                    ...judgments,
                    adjustment_strategy_is_valid:
                      e.target.value === ''
                        ? undefined
                        : e.target.value === 'true'
                  })
                }
              >
                <option value="">Not applicable</option>
                <option value="true">Yes</option>
                <option value="false">No</option>
              </select>
            </div>
          </div>

          {/* Assessment Results */}
          <div className="jp-jupyterlab-research-assistant-wwc-copilot-wwc-results">
            <h3>Assessment Results</h3>

            {/* Final Rating */}
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

            {/* Attrition Section */}
            {assessment.overall_attrition !== undefined && (
              <div className="jp-jupyterlab-research-assistant-wwc-copilot-wwc-section">
                <h4>Attrition</h4>
                <p>
                  Overall: {(assessment.overall_attrition * 100).toFixed(1)}%
                </p>
                {assessment.differential_attrition !== undefined && (
                  <p>
                    Differential:{' '}
                    {(assessment.differential_attrition * 100).toFixed(1)}%
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

            {/* Baseline Equivalence Section */}
            {assessment.baseline_effect_size !== undefined && (
              <div className="jp-jupyterlab-research-assistant-wwc-copilot-wwc-section">
                <h4>Baseline Equivalence</h4>
                <p>
                  Effect Size (Cohen's d):{' '}
                  {assessment.baseline_effect_size.toFixed(3)}
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
            )}

            {/* Justification */}
            <div className="jp-jupyterlab-research-assistant-wwc-copilot-wwc-justification">
              <h4>Justification</h4>
              <ul>
                {assessment.rating_justification.map((reason, idx) => (
                  <li key={idx}>{reason}</li>
                ))}
              </ul>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
