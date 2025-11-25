import React from 'react';
import { IMetaAnalysisResult } from '../api';
import { formatPercent, formatNumber, formatCI } from '../utils/format';

interface MetaAnalysisViewProps {
  result: IMetaAnalysisResult;
}

export const MetaAnalysisView: React.FC<MetaAnalysisViewProps> = ({
  result
}) => {
  return (
    <div className="jp-jupyterlab-research-assistant-wwc-copilot-meta-analysis">
      <h3>Meta-Analysis Results</h3>

      {/* Summary Statistics */}
      <div className="jp-jupyterlab-research-assistant-wwc-copilot-meta-analysis-summary">
        <div className="jp-jupyterlab-research-assistant-wwc-copilot-meta-analysis-stat">
          <strong>Pooled Effect Size:</strong>
          <span>d = {formatNumber(result.pooled_effect, 3)}</span>
        </div>
        <div className="jp-jupyterlab-research-assistant-wwc-copilot-meta-analysis-stat">
          <strong>95% Confidence Interval:</strong>
          <span>{formatCI(result.ci_lower, result.ci_upper, 3)}</span>
        </div>
        <div className="jp-jupyterlab-research-assistant-wwc-copilot-meta-analysis-stat">
          <strong>P-value:</strong>
          <span>{formatNumber(result.p_value, 4)}</span>
        </div>
        <div className="jp-jupyterlab-research-assistant-wwc-copilot-meta-analysis-stat">
          <strong>I² (Heterogeneity):</strong>
          <span>
            {formatNumber(result.i_squared, 1)}% -{' '}
            {result.heterogeneity_interpretation || 'N/A'}
          </span>
        </div>
        <div className="jp-jupyterlab-research-assistant-wwc-copilot-meta-analysis-stat">
          <strong>Number of Studies:</strong>
          <span>{result.n_studies}</span>
        </div>
      </div>

      {/* Forest Plot */}
      {result.forest_plot && (
        <div className="jp-jupyterlab-research-assistant-wwc-copilot-meta-analysis-plot">
          <h4>Forest Plot</h4>
          <img
            src={`data:image/png;base64,${result.forest_plot}`}
            alt="Forest Plot"
            style={{ maxWidth: '100%', height: 'auto' }}
          />
        </div>
      )}

      {/* Individual Study Results */}
      <div className="jp-jupyterlab-research-assistant-wwc-copilot-meta-analysis-studies">
        <h4>Individual Studies</h4>
        <table className="jp-jupyterlab-research-assistant-wwc-copilot-table">
          <thead>
            <tr>
              <th>Study</th>
              <th>Effect Size</th>
              <th>95% CI</th>
              <th>Weight</th>
            </tr>
          </thead>
          <tbody>
            {result.studies.map((study, idx) => (
              <tr key={idx}>
                <td>{study.study_label}</td>
                <td>{formatNumber(study.effect_size, 3)}</td>
                <td>{formatCI(study.ci_lower, study.ci_upper, 3)}</td>
                <td>{formatPercent(study.weight, 1)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
