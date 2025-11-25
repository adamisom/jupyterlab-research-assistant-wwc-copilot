import React from 'react';
import { IPaper } from '../api';

interface IPaperCardProps {
  paper: IPaper;
  onImport?: () => void;
  onViewDetails?: () => void;
  selected?: boolean;
  onToggleSelection?: () => void;
}

export const PaperCard: React.FC<IPaperCardProps> = ({
  paper,
  onImport,
  onViewDetails,
  selected = false,
  onToggleSelection
}) => {
  return (
    <div
      className={`jp-jupyterlab-research-assistant-wwc-copilot-paper-card ${
        selected
          ? 'jp-jupyterlab-research-assistant-wwc-copilot-paper-card-selected'
          : ''
      }`}
    >
      {onToggleSelection && (
        <div className="jp-jupyterlab-research-assistant-wwc-copilot-paper-card-checkbox">
          <input
            type="checkbox"
            checked={selected}
            onChange={onToggleSelection}
            className="jp-jupyterlab-research-assistant-wwc-copilot-checkbox"
            onClick={e => e.stopPropagation()}
          />
        </div>
      )}
      <h3
        className="jp-jupyterlab-research-assistant-wwc-copilot-paper-title"
        onClick={onViewDetails}
        style={{ cursor: onViewDetails ? 'pointer' : 'default' }}
      >
        {paper.title}
      </h3>
      <div className="jp-jupyterlab-research-assistant-wwc-copilot-paper-meta">
        {paper.authors && paper.authors.length > 0 && (
          <div className="jp-jupyterlab-research-assistant-wwc-copilot-paper-authors">
            Authors: {paper.authors.join(', ')}
          </div>
        )}
        {paper.year && (
          <div className="jp-jupyterlab-research-assistant-wwc-copilot-paper-year">
            Year: {paper.year}
          </div>
        )}
        {paper.citation_count !== undefined && (
          <div className="jp-jupyterlab-research-assistant-wwc-copilot-paper-citations">
            Citations: {paper.citation_count}
          </div>
        )}
      </div>
      {paper.abstract && (
        <div className="jp-jupyterlab-research-assistant-wwc-copilot-paper-abstract">
          {paper.abstract.substring(0, 200)}
          {paper.abstract.length > 200 ? '...' : ''}
        </div>
      )}
      <div style={{ display: 'flex', gap: '8px', marginTop: '8px' }}>
        {onViewDetails && (
          <button
            onClick={onViewDetails}
            className="jp-jupyterlab-research-assistant-wwc-copilot-button"
          >
            View Details
          </button>
        )}
        {onImport && (
          <button
            onClick={onImport}
            className="jp-jupyterlab-research-assistant-wwc-copilot-button jp-jupyterlab-research-assistant-wwc-copilot-import-button"
          >
            Import to Library
          </button>
        )}
      </div>
    </div>
  );
};
