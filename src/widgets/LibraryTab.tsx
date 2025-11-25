import React, { useState, useEffect, useRef } from 'react';
import {
  IPaper,
  getLibrary,
  searchLibrary,
  importPDF,
  exportLibrary
} from '../api';
import { PaperCard } from './PaperCard';
import { showError, showSuccess } from '../utils/notifications';
import { SkeletonLoader } from './SkeletonLoader';
import { DetailView } from './DetailView';

export const LibraryTab: React.FC = () => {
  const [papers, setPapers] = useState<IPaper[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedPaper, setSelectedPaper] = useState<IPaper | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    loadLibrary();
  }, []);

  const loadLibrary = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getLibrary();
      setPapers(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load library');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileSelect = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }

    // Validate file type
    if (file.type !== 'application/pdf' && !file.name.endsWith('.pdf')) {
      setError('Please select a PDF file');
      return;
    }

    // Validate file size (max 50MB)
    if (file.size > 50 * 1024 * 1024) {
      setError('File size must be less than 50MB');
      return;
    }

    setIsUploading(true);
    setError(null);

    try {
      const importedPaper = await importPDF(file);
      // Refresh library to show new paper
      await loadLibrary();
      showSuccess(
        'PDF Uploaded',
        `Successfully imported: ${importedPaper.title}`
      );
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : 'PDF upload failed';
      setError(errorMessage);
      showError(
        'PDF Upload Failed',
        errorMessage,
        err instanceof Error ? err : undefined
      );
    } finally {
      setIsUploading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      loadLibrary();
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const results = await searchLibrary(searchQuery);
      setPapers(results);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed');
    } finally {
      setIsLoading(false);
    }
  };

  if (selectedPaper) {
    return (
      <DetailView
        paper={selectedPaper}
        onClose={() => setSelectedPaper(null)}
      />
    );
  }

  return (
    <div className="jp-jupyterlab-research-assistant-wwc-copilot-library">
      <div className="jp-jupyterlab-research-assistant-wwc-copilot-search-bar">
        <input
          type="text"
          value={searchQuery}
          onChange={e => setSearchQuery(e.target.value)}
          onKeyPress={e => {
            if (e.key === 'Enter') {
              handleSearch();
            }
          }}
          placeholder="Search your library..."
          className="jp-jupyterlab-research-assistant-wwc-copilot-input"
        />
        <button
          onClick={handleSearch}
          disabled={isLoading}
          className="jp-jupyterlab-research-assistant-wwc-copilot-button"
        >
          Search
        </button>
        <select
          onChange={async e => {
            const format = e.target.value as 'json' | 'csv' | 'bibtex' | '';
            if (format) {
              try {
                await exportLibrary(format);
                showSuccess(
                  'Export Complete',
                  `Library exported as ${format.toUpperCase()}`
                );
              } catch (err) {
                showError(
                  'Export Failed',
                  err instanceof Error ? err.message : 'Unknown error'
                );
              }
              e.target.value = ''; // Reset
            }
          }}
          className="jp-jupyterlab-research-assistant-wwc-copilot-select"
        >
          <option value="">Export...</option>
          <option value="json">Export as JSON</option>
          <option value="csv">Export as CSV</option>
          <option value="bibtex">Export as BibTeX</option>
        </select>
      </div>

      {/* PDF Upload Section */}
      <div className="jp-jupyterlab-research-assistant-wwc-copilot-upload-section">
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,application/pdf"
          onChange={handleFileSelect}
          style={{ display: 'none' }}
          id="pdf-upload-input"
        />
        <label
          htmlFor="pdf-upload-input"
          className="jp-jupyterlab-research-assistant-wwc-copilot-button"
          style={{ display: 'inline-block', cursor: 'pointer' }}
        >
          {isUploading ? 'Uploading...' : 'Upload PDF'}
        </label>
      </div>

      {error && (
        <div className="jp-jupyterlab-research-assistant-wwc-copilot-error">
          Error: {error}
        </div>
      )}

      {isLoading && (
        <div>
          <SkeletonLoader />
          <SkeletonLoader />
          <SkeletonLoader />
        </div>
      )}

      <div className="jp-jupyterlab-research-assistant-wwc-copilot-papers">
        {papers.length === 0 && !isLoading && (
          <div className="jp-jupyterlab-research-assistant-wwc-copilot-empty">
            No papers found. Use the Discovery tab to search and import papers,
            or upload a PDF above.
          </div>
        )}
        {papers.map(paper => (
          <PaperCard
            key={paper.id}
            paper={paper}
            onViewDetails={() => setSelectedPaper(paper)}
          />
        ))}
      </div>
    </div>
  );
};
