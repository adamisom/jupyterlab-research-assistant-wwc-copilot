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
    <div className="jp-WWCExtension-conflicts">
      <h3>Conflict Detection Results</h3>

      {result.status === 'disabled' && result.message && (
        <div className="jp-WWCExtension-error" style={{ marginBottom: '16px' }}>
          <strong>Conflict Detection Unavailable</strong>
          <p>{result.message}</p>
        </div>
      )}

      {result.message && result.status === 'success' && (
        <div
          className="jp-WWCExtension-loading"
          style={{
            marginBottom: '16px',
            padding: '12px',
            backgroundColor: 'var(--jp-layout-color2)',
            borderRadius: 'var(--jp-border-radius)'
          }}
        >
          <p>{result.message}</p>
        </div>
      )}

      <div className="jp-WWCExtension-conflicts-summary">
        <p>
          Found <strong>{result.n_contradictions}</strong> contradictions across{' '}
          <strong>{result.n_papers}</strong> papers.
        </p>
      </div>

      {/* Findings Preview */}
      {hasFindings && (
        <div className="jp-WWCExtension-findings-preview">
          <h4>Extracted Key Findings</h4>
          {Object.entries(result.findings!).map(([paperId, paperFindings]) => (
            <div key={paperId} className="jp-WWCExtension-finding-item">
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
        <div className="jp-WWCExtension-conflicts-empty">
          No contradictions detected.
        </div>
      ) : (
        <div className="jp-WWCExtension-conflicts-list">
          {result.contradictions.map((conflict, idx) => (
            <div key={idx} className="jp-WWCExtension-conflict-item">
              <div className="jp-WWCExtension-conflict-header">
                <strong>Contradiction #{idx + 1}</strong>
                <span>Confidence: {formatPercent(conflict.confidence, 1)}</span>
              </div>
              {conflict.paper1_title && conflict.paper2_title && (
                <div className="jp-WWCExtension-conflict-papers">
                  <div>
                    <strong>Paper 1:</strong> {conflict.paper1_title}
                  </div>
                  <div>
                    <strong>Paper 2:</strong> {conflict.paper2_title}
                  </div>
                </div>
              )}
              <div className="jp-WWCExtension-conflict-findings">
                <div>
                  <strong>Finding 1:</strong> {conflict.finding1}
                </div>
                <div>
                  <strong>Finding 2:</strong> {conflict.finding2}
                </div>
              </div>
              <div className="jp-WWCExtension-conflict-explanation">
                <strong>Why this was flagged:</strong>
                <p>
                  The NLI model detected a contradiction with{' '}
                  {formatPercent(conflict.confidence, 1)} confidence. This means
                  the model determined that these two findings cannot both be
                  true simultaneously.
                </p>
                <p>
                  <strong>Note:</strong> Not all flagged contradictions
                  represent genuine conflicts. The model may flag findings that:
                </p>
                <ul>
                  <li>
                    Address different topics or interventions (e.g., peer
                    tutoring vs. multimedia instruction)
                  </li>
                  <li>
                    Use different methodologies or study different populations
                  </li>
                  <li>
                    Make claims that are logically incompatible (true
                    contradictions)
                  </li>
                </ul>
                <p>
                  <strong>Review carefully:</strong> Consider whether these
                  findings actually contradict each other, or if they simply
                  describe different studies with different interventions or
                  contexts.
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
