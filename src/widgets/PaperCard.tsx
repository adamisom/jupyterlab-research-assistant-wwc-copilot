import React from 'react';
import { IPaper } from '../api';
import { hasFullPDF } from '../utils/paper';

interface PaperCardProps {
  paper: IPaper;
  onImport?: () => void;
  onViewDetails?: () => void;
  selected?: boolean;
  onToggleSelection?: () => void;
}

export const PaperCard: React.FC<PaperCardProps> = ({
  paper,
  onImport,
  onViewDetails,
  selected = false,
  onToggleSelection
}) => {
  return (
    <div
      className={`jp-WWCExtension-paper-card ${
        selected ? 'jp-WWCExtension-paper-card-selected' : ''
      }`}
    >
      <div className="jp-WWCExtension-paper-card-header">
        {onToggleSelection && (
          <div className="jp-WWCExtension-paper-card-checkbox">
            <input
              type="checkbox"
              checked={selected}
              onChange={onToggleSelection}
              className="jp-WWCExtension-checkbox"
              onClick={e => e.stopPropagation()}
            />
          </div>
        )}
        {onViewDetails && (
          <button
            onClick={onViewDetails}
            className="jp-WWCExtension-button jp-WWCExtension-view-details-button"
          >
            View Details
          </button>
        )}
      </div>
      <h3
        className={`jp-WWCExtension-paper-title ${
          onViewDetails ? 'jp-mod-clickable' : ''
        }`}
        onClick={onViewDetails}
      >
        {paper.title}
      </h3>
      <div className="jp-WWCExtension-paper-meta">
        {paper.authors && paper.authors.length > 0 && (
          <div className="jp-WWCExtension-paper-authors">
            Authors: {paper.authors.join(', ')}
          </div>
        )}
        {paper.year && (
          <div className="jp-WWCExtension-paper-year">Year: {paper.year}</div>
        )}
        {paper.citation_count !== undefined && (
          <div className="jp-WWCExtension-paper-citations">
            Citations: {paper.citation_count}
          </div>
        )}
      </div>
      {paper.abstract && (
        <div className="jp-WWCExtension-paper-abstract">
          {paper.abstract.substring(0, 200)}
          {paper.abstract.length > 200 ? '...' : ''}
        </div>
      )}
      <div className="jp-WWCExtension-paper-status">
        {hasFullPDF(paper) ? (
          <span className="jp-WWCExtension-pdf-badge jp-mod-has-pdf">
            📄 Full PDF
          </span>
        ) : (
          <span className="jp-WWCExtension-pdf-badge jp-mod-metadata-only">
            📋 Metadata Only
          </span>
        )}
      </div>
      <div className="jp-WWCExtension-paper-actions">
        {onImport && (
          <button
            onClick={onImport}
            className="jp-WWCExtension-button jp-WWCExtension-import-button"
          >
            Import to Library
          </button>
        )}
      </div>
    </div>
  );
};
