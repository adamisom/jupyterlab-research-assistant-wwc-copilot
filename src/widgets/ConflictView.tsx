import React from 'react';
import { IConflictDetectionResult } from '../api';

interface IConflictViewProps {
  result: IConflictDetectionResult;
}

export const ConflictView: React.FC<IConflictViewProps> = ({ result }) => {
  return (
    <div className="jp-jupyterlab-research-assistant-wwc-copilot-conflicts">
      <h3>Conflict Detection Results</h3>

      <div className="jp-jupyterlab-research-assistant-wwc-copilot-conflicts-summary">
        <p>
          Found <strong>{result.n_contradictions}</strong> contradictions across{' '}
          <strong>{result.n_papers}</strong> papers.
        </p>
      </div>

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
                <span>
                  Confidence: {(conflict.confidence * 100).toFixed(1)}%
                </span>
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
