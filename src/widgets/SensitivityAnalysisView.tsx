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
    <div className="jp-jupyterlab-research-assistant-wwc-copilot-sensitivity-analysis">
      <h3>Sensitivity Analysis</h3>

      {/* Overall Effect */}
      <div className="jp-jupyterlab-research-assistant-wwc-copilot-sensitivity-overall">
        <h4>Overall Effect (All Studies)</h4>
        <div className="jp-jupyterlab-research-assistant-wwc-copilot-meta-analysis-summary">
          <div className="jp-jupyterlab-research-assistant-wwc-copilot-meta-analysis-stat">
            <strong>Pooled Effect:</strong>
            <span>{formatNumber(result.overall_effect, 3)}</span>
          </div>
        </div>
      </div>

      {/* Leave-One-Out Results */}
      <div className="jp-jupyterlab-research-assistant-wwc-copilot-sensitivity-loo">
        <h4>Leave-One-Out Analysis</h4>
        <p>Effect size when each study is removed:</p>
        <div className="jp-jupyterlab-research-assistant-wwc-copilot-meta-analysis-studies">
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
                  <td>{formatNumber(loo.pooled_effect, 3)}</td>
                  <td>{formatCI(loo.ci_lower, loo.ci_upper, 3)}</td>
                  <td
                    style={{
                      color:
                        Math.abs(loo.difference_from_overall) > 0.2
                          ? '#f44336'
                          : 'inherit'
                    }}
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
      <div className="jp-jupyterlab-research-assistant-wwc-copilot-sensitivity-influence">
        <h4>Influence Diagnostics</h4>
        <p>Studies ranked by influence on overall result:</p>
        <div className="jp-jupyterlab-research-assistant-wwc-copilot-meta-analysis-studies">
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
