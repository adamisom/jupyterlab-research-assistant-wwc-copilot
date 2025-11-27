import React from 'react';
import { ServerConnection } from '@jupyterlab/services';
import { URLExt } from '@jupyterlab/coreutils';
import { IPaper } from '../api';
import { hasFullPDF } from '../utils/paper';
import { openPDFInNewTab } from '../utils/download';
import { showError } from '../utils/notifications';

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
        <div className="jp-WWCExtension-paper-authors">
          Authors:{' '}
          {paper.authors && paper.authors.length > 0
            ? paper.authors.join(', ')
            : 'could not detect'}
        </div>
        <div className="jp-WWCExtension-paper-year">
          Year: {paper.year ? paper.year : 'could not detect'}
        </div>
        {paper.citation_count !== undefined && paper.citation_count > 0 && (
          <div className="jp-WWCExtension-paper-citations">
            Citations: {paper.citation_count}
          </div>
        )}
      </div>
      <div className="jp-WWCExtension-paper-status">
        {hasFullPDF(paper) ? (
          <a
            href="#"
            className="jp-WWCExtension-pdf-badge jp-mod-has-pdf"
            onClick={async e => {
              e.preventDefault();
              e.stopPropagation();
              if (paper.id !== undefined) {
                try {
                  const settings = ServerConnection.makeSettings();
                  const url = URLExt.join(
                    settings.baseUrl,
                    'jupyterlab-research-assistant-wwc-copilot',
                    'pdf',
                    `?paper_id=${paper.id}`
                  );
                  await openPDFInNewTab(url);
                } catch (err) {
                  showError(
                    'Failed to Open PDF',
                    err instanceof Error
                      ? err.message
                      : 'Unknown error occurred',
                    err instanceof Error ? err : undefined
                  );
                }
              }
            }}
          >
            📄 Full Local PDF
          </a>
        ) : paper.open_access_pdf ? (
          <a
            href={paper.open_access_pdf}
            target="_blank"
            rel="noopener noreferrer"
            className="jp-WWCExtension-pdf-badge jp-mod-open-access"
            onClick={e => e.stopPropagation()}
          >
            📥 Open Access PDF
          </a>
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
