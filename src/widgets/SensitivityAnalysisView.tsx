import React from 'react';
import { ISensitivityAnalysisResult } from '../api';
import { formatNumber, formatCI } from '../utils/format';

interface SensitivityAnalysisViewProps {
  result: ISensitivityAnalysisResult;
}

export const SensitivityAnalysisView: React.FC<
  SensitivityAnalysisViewProps
> = ({ result }) => {
  return (
    <div className="jp-WWCExtension-sensitivity-analysis">
      <h3>Sensitivity Analysis</h3>

      {/* Overall Effect */}
      <div className="jp-WWCExtension-sensitivity-overall">
        <h4>Overall Effect (All Studies)</h4>
        <div className="jp-WWCExtension-meta-analysis-summary">
          <div className="jp-WWCExtension-meta-analysis-stat">
            <strong>Pooled Effect:</strong>
            <span>{formatNumber(result.overall_effect, 3)}</span>
          </div>
        </div>
      </div>

      {/* Leave-One-Out Results */}
      <div className="jp-WWCExtension-sensitivity-loo">
        <h4>Leave-One-Out Analysis</h4>
        <p>Effect size when each study is removed:</p>
        <div className="jp-WWCExtension-meta-analysis-studies">
          <table className="jp-WWCExtension-table">
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
                  <td>{formatNumber(loo.pooled_effect, 3)}</td>
                  <td>{formatCI(loo.ci_lower, loo.ci_upper, 3)}</td>
                  <td
                    className={
                      Math.abs(loo.difference_from_overall) > 0.2
                        ? 'jp-mod-high-difference'
                        : ''
                    }
                  >
                    {loo.difference_from_overall > 0 ? '+' : ''}
                    {formatNumber(loo.difference_from_overall, 3)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Influence Diagnostics */}
      <div className="jp-WWCExtension-sensitivity-influence">
        <h4>Influence Diagnostics</h4>
        <p>Studies ranked by influence on overall result:</p>
        <div className="jp-WWCExtension-meta-analysis-studies">
          <table className="jp-WWCExtension-table">
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
                  <td>{formatNumber(diag.influence_score, 4)}</td>
                  <td>{(diag.weight * 100).toFixed(1)}%</td>
                  <td>{formatNumber(diag.effect_size, 3)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
