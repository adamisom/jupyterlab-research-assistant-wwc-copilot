import React from 'react';
import { IPaper } from '../api';

interface IPaperCardProps {
  paper: IPaper;
  onImport?: () => void;
}

export const PaperCard: React.FC<IPaperCardProps> = ({ paper, onImport }) => {
  return (
    <div className="jp-jupyterlab-research-assistant-wwc-copilot-paper-card">
      <h3 className="jp-jupyterlab-research-assistant-wwc-copilot-paper-title">
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
      {onImport && (
        <button
          onClick={onImport}
          className="jp-jupyterlab-research-assistant-wwc-copilot-button jp-jupyterlab-research-assistant-wwc-copilot-import-button"
        >
          Import to Library
        </button>
      )}
    </div>
  );
};
