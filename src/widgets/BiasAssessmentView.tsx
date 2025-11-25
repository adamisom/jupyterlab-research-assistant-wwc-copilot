import React from 'react';
import { IBiasAssessmentResult } from '../api';

interface BiasAssessmentViewProps {
  result: IBiasAssessmentResult;
}

export const BiasAssessmentView: React.FC<BiasAssessmentViewProps> = ({
  result
}) => {
  return (
    <div className="jp-jupyterlab-research-assistant-wwc-copilot-bias-assessment">
      <h3>Publication Bias Assessment</h3>

      {/* Egger's Test Results */}
      <div className="jp-jupyterlab-research-assistant-wwc-copilot-eggers-test">
        <h4>Egger's Test</h4>
        {result.eggers_test.intercept_pvalue !== null ? (
          <div className="jp-jupyterlab-research-assistant-wwc-copilot-meta-analysis-summary">
            <div className="jp-jupyterlab-research-assistant-wwc-copilot-meta-analysis-stat">
              <strong>Intercept:</strong>
              <span>
                {result.eggers_test.intercept !== null
                  ? result.eggers_test.intercept.toFixed(4)
                  : 'N/A'}
              </span>
            </div>
            <div className="jp-jupyterlab-research-assistant-wwc-copilot-meta-analysis-stat">
              <strong>Standard Error:</strong>
              <span>
                {result.eggers_test.intercept_se !== null
                  ? result.eggers_test.intercept_se.toFixed(4)
                  : 'N/A'}
              </span>
            </div>
            <div className="jp-jupyterlab-research-assistant-wwc-copilot-meta-analysis-stat">
              <strong>P-value:</strong>
              <span>{result.eggers_test.intercept_pvalue.toFixed(4)}</span>
            </div>
            <div className="jp-jupyterlab-research-assistant-wwc-copilot-meta-analysis-stat">
              <strong>Interpretation:</strong>
              <span>{result.eggers_test.interpretation}</span>
            </div>
          </div>
        ) : (
          <p>{result.eggers_test.interpretation}</p>
        )}
      </div>

      {/* Funnel Plot */}
      {result.funnel_plot && (
        <div className="jp-jupyterlab-research-assistant-wwc-copilot-funnel-plot">
          <h4>Funnel Plot</h4>
          <div className="jp-jupyterlab-research-assistant-wwc-copilot-meta-analysis-plot">
            <img
              src={`data:image/png;base64,${result.funnel_plot}`}
              alt="Funnel Plot"
              style={{ maxWidth: '100%', height: 'auto' }}
            />
          </div>
        </div>
      )}
    </div>
  );
};
