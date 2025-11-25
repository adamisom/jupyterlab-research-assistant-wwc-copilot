import React from 'react';
import { IPaper } from '../api';

interface IDetailViewProps {
  paper: IPaper;
  onClose: () => void;
}

export const DetailView: React.FC<IDetailViewProps> = ({ paper, onClose }) => {
  const [activeTab, setActiveTab] = React.useState<
    'overview' | 'study' | 'learning' | 'wwc'
  >('overview');

  const openPDF = () => {
    if (paper.pdf_path) {
      // Open PDF in new tab (if accessible via JupyterLab file browser)
      window.open(`/files${paper.pdf_path}`, '_blank');
    }
  };

  return (
    <div className="jp-jupyterlab-research-assistant-wwc-copilot-detail-view">
      <div className="jp-jupyterlab-research-assistant-wwc-copilot-detail-header">
        <button
          onClick={onClose}
          className="jp-jupyterlab-research-assistant-wwc-copilot-close-button"
        >
          ×
        </button>
        <h2>{paper.title}</h2>
        <div className="jp-jupyterlab-research-assistant-wwc-copilot-detail-meta">
          {paper.authors && paper.authors.length > 0 && (
            <div>Authors: {paper.authors.join(', ')}</div>
          )}
          {paper.year && <div>Year: {paper.year}</div>}
          {paper.doi && <div>DOI: {paper.doi}</div>}
          {paper.citation_count !== undefined && (
            <div>Citations: {paper.citation_count}</div>
          )}
        </div>
      </div>

      <div className="jp-jupyterlab-research-assistant-wwc-copilot-detail-tabs">
        <button
          className={activeTab === 'overview' ? 'active' : ''}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        {paper.study_metadata && (
          <button
            className={activeTab === 'study' ? 'active' : ''}
            onClick={() => setActiveTab('study')}
          >
            Study Metadata
          </button>
        )}
        {paper.learning_science_metadata && (
          <button
            className={activeTab === 'learning' ? 'active' : ''}
            onClick={() => setActiveTab('learning')}
          >
            Learning Science
          </button>
        )}
      </div>

      <div className="jp-jupyterlab-research-assistant-wwc-copilot-detail-content">
        {activeTab === 'overview' && (
          <div>
            {paper.abstract && (
              <div className="jp-jupyterlab-research-assistant-wwc-copilot-detail-section">
                <h3>Abstract</h3>
                <p>{paper.abstract}</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'study' && paper.study_metadata && (
          <div>
            <div className="jp-jupyterlab-research-assistant-wwc-copilot-detail-section">
              <h3>Methodology</h3>
              <p>{paper.study_metadata.methodology || 'Not specified'}</p>
            </div>
            <div className="jp-jupyterlab-research-assistant-wwc-copilot-detail-section">
              <h3>Sample Sizes</h3>
              <p>
                Baseline: {paper.study_metadata.sample_size_baseline || 'N/A'}
              </p>
              <p>
                Endline: {paper.study_metadata.sample_size_endline || 'N/A'}
              </p>
            </div>
            {paper.study_metadata.effect_sizes && (
              <div className="jp-jupyterlab-research-assistant-wwc-copilot-detail-section">
                <h3>Effect Sizes</h3>
                <table>
                  <thead>
                    <tr>
                      <th>Outcome</th>
                      <th>Cohen's d</th>
                      <th>Standard Error</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(paper.study_metadata.effect_sizes).map(
                      ([outcome, es]) => (
                        <tr key={outcome}>
                          <td>{outcome}</td>
                          <td>{es.d.toFixed(2)}</td>
                          <td>{es.se.toFixed(2)}</td>
                        </tr>
                      )
                    )}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {activeTab === 'learning' && paper.learning_science_metadata && (
          <div>
            <div className="jp-jupyterlab-research-assistant-wwc-copilot-detail-section">
              <h3>Learning Domain</h3>
              <p>
                {paper.learning_science_metadata.learning_domain ||
                  'Not specified'}
              </p>
            </div>
            <div className="jp-jupyterlab-research-assistant-wwc-copilot-detail-section">
              <h3>Intervention Type</h3>
              <p>
                {paper.learning_science_metadata.intervention_type ||
                  'Not specified'}
              </p>
            </div>
          </div>
        )}
      </div>

      <div className="jp-jupyterlab-research-assistant-wwc-copilot-detail-actions">
        {paper.pdf_path && (
          <button
            onClick={openPDF}
            className="jp-jupyterlab-research-assistant-wwc-copilot-button"
          >
            Open PDF
          </button>
        )}
      </div>
    </div>
  );
};
