import React from 'react';
import {
  IConflictDetectionResult,
  IConflictDetectionWithFindingsResult
} from '../api';
import { formatPercent } from '../utils/format';

interface ConflictViewProps {
  result: IConflictDetectionResult | IConflictDetectionWithFindingsResult;
}

export const ConflictView: React.FC<ConflictViewProps> = ({ result }) => {
  const hasFindings =
    'findings' in result &&
    result.findings &&
    Object.keys(result.findings).length > 0;

  return (
    <div className="jp-jupyterlab-research-assistant-wwc-copilot-conflicts">
      <h3>Conflict Detection Results</h3>

      <div className="jp-jupyterlab-research-assistant-wwc-copilot-conflicts-summary">
        <p>
          Found <strong>{result.n_contradictions}</strong> contradictions across{' '}
          <strong>{result.n_papers}</strong> papers.
        </p>
      </div>

      {/* Findings Preview */}
      {hasFindings && (
        <div className="jp-jupyterlab-research-assistant-wwc-copilot-findings-preview">
          <h4>Extracted Key Findings</h4>
          {Object.entries(result.findings!).map(([paperId, paperFindings]) => (
            <div
              key={paperId}
              className="jp-jupyterlab-research-assistant-wwc-copilot-finding-item"
            >
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

      {result.contradictions.length === 0 ? (
        <div className="jp-jupyterlab-research-assistant-wwc-copilot-conflicts-empty">
          No contradictions detected.
        </div>
      ) : (
        <div className="jp-jupyterlab-research-assistant-wwc-copilot-conflicts-list">
          {result.contradictions.map((conflict, idx) => (
            <div
              key={idx}
              className="jp-jupyterlab-research-assistant-wwc-copilot-conflict-item"
            >
              <div className="jp-jupyterlab-research-assistant-wwc-copilot-conflict-header">
                <strong>Contradiction #{idx + 1}</strong>
                <span>Confidence: {formatPercent(conflict.confidence, 1)}</span>
              </div>
              {conflict.paper1_title && conflict.paper2_title && (
                <div className="jp-jupyterlab-research-assistant-wwc-copilot-conflict-papers">
                  <div>
                    <strong>Paper 1:</strong> {conflict.paper1_title}
                  </div>
                  <div>
                    <strong>Paper 2:</strong> {conflict.paper2_title}
                  </div>
                </div>
              )}
              <div className="jp-jupyterlab-research-assistant-wwc-copilot-conflict-findings">
                <div>
                  <strong>Finding 1:</strong> {conflict.finding1}
                </div>
                <div>
                  <strong>Finding 2:</strong> {conflict.finding2}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
