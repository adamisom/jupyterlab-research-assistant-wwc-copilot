import React from 'react';
import { ServerConnection } from '@jupyterlab/services';
import { URLExt } from '@jupyterlab/coreutils';
import { IPaper } from '../api';
import { AppEvents } from '../utils/events';
import { Tabs } from './Tabs';
import { formatNumber } from '../utils/format';

interface DetailViewProps {
  paper: IPaper;
  onClose: () => void;
}

export const DetailView: React.FC<DetailViewProps> = ({ paper, onClose }) => {
  const [activeTab, setActiveTab] = React.useState<
    'overview' | 'study' | 'learning' | 'wwc'
  >('overview');

  const openPDF = () => {
    if (paper.id !== undefined) {
      // Open PDF via our backend route
      const settings = ServerConnection.makeSettings();
      const url = URLExt.join(
        settings.baseUrl,
        'jupyterlab-research-assistant-wwc-copilot',
        'pdf',
        `?paper_id=${paper.id}`
      );
      window.open(url, '_blank');
    }
  };

  return (
    <div className="jp-WWCExtension-detail-view">
      <div className="jp-WWCExtension-detail-header">
        <div
          style={{
            display: 'flex',
            gap: '10px',
            alignItems: 'center',
            marginBottom: '8px'
          }}
        >
          <button onClick={onClose} className="jp-WWCExtension-button">
            ← Go Back
          </button>
          {paper.id !== undefined && (
            <button
              onClick={() => {
                AppEvents.dispatchOpenWWCCopilot(paper.id!, paper.title);
              }}
              className="jp-WWCExtension-button"
            >
              Open WWC Co-Pilot
            </button>
          )}
        </div>
        <h2>{paper.title}</h2>
        <div className="jp-WWCExtension-detail-meta">
          {paper.authors && paper.authors.length > 0 && (
            <div>
              Authors:{' '}
              {paper.authors
                .map(author => {
                  if (typeof author === 'string') {
                    return author;
                  }
                  // Handle case where author might be an object (for backwards compatibility)
                  return (author as any)?.name || 'Unknown';
                })
                .join(', ')}
            </div>
          )}
          {paper.year && <div>Year: {paper.year}</div>}
          {paper.doi && <div>DOI: {paper.doi}</div>}
          {paper.citation_count !== undefined && (
            <div>Citations: {paper.citation_count}</div>
          )}
        </div>
      </div>

      <Tabs
        tabs={[
          { id: 'overview', label: 'Overview' },
          ...(paper.study_metadata
            ? [{ id: 'study', label: 'Study Metadata' }]
            : []),
          ...(paper.learning_science_metadata
            ? [{ id: 'learning', label: 'Learning Science' }]
            : [])
        ]}
        activeTab={activeTab}
        onTabChange={(tabId: string) =>
          setActiveTab(tabId as 'overview' | 'study' | 'learning' | 'wwc')
        }
        className="jp-WWCExtension-detail-tabs"
        activeClassName="active"
        inactiveClassName=""
      />

      <div className="jp-WWCExtension-detail-content">
        {activeTab === 'overview' && (
          <div>
            {paper.abstract ? (
              <div className="jp-WWCExtension-detail-section">
                <h3>Abstract</h3>
                <p>{paper.abstract}</p>
              </div>
            ) : (
              <div className="jp-WWCExtension-detail-section">
                <p
                  style={{
                    color: 'var(--jp-content-font-color2)',
                    fontStyle: 'italic'
                  }}
                >
                  No abstract available for this paper.
                </p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'study' && paper.study_metadata && (
          <div>
            <div className="jp-WWCExtension-detail-section">
              <h3>Methodology</h3>
              <p>{paper.study_metadata.methodology || 'Not specified'}</p>
            </div>
            <div className="jp-WWCExtension-detail-section">
              <h3>Sample Sizes</h3>
              <p>
                Baseline: {paper.study_metadata.sample_size_baseline || 'N/A'}
              </p>
              <p>
                Endline: {paper.study_metadata.sample_size_endline || 'N/A'}
              </p>
            </div>
            {paper.study_metadata.effect_sizes && (
              <div className="jp-WWCExtension-detail-section">
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
                          <td>{formatNumber(es.d, 2)}</td>
                          <td>{formatNumber(es.se, 2)}</td>
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
            <div className="jp-WWCExtension-detail-section">
              <h3>Learning Domain</h3>
              <p>
                {paper.learning_science_metadata.learning_domain ||
                  'Not specified'}
              </p>
            </div>
            <div className="jp-WWCExtension-detail-section">
              <h3>Intervention Type</h3>
              <p>
                {paper.learning_science_metadata.intervention_type ||
                  'Not specified'}
              </p>
            </div>
          </div>
        )}
      </div>

      <div className="jp-WWCExtension-detail-actions">
        {paper.pdf_path && (
          <button onClick={openPDF} className="jp-WWCExtension-button">
            Open PDF
          </button>
        )}
      </div>
    </div>
  );
};
