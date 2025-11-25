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
import { SearchBar } from './SearchBar';
import { ErrorDisplay } from './ErrorDisplay';
import { LoadingState } from './LoadingState';
import { DetailView } from './DetailView';
import { getPaperKey } from '../utils/paper';
import { AppEvents } from '../utils/events';

export const LibraryTab: React.FC = () => {
  const [papers, setPapers] = useState<IPaper[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedPaper, setSelectedPaper] = useState<IPaper | null>(null);
  const [selectedPapers, setSelectedPapers] = useState<Set<number>>(new Set());
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
      // Get AI config from settings if available
      // For now, pass undefined - settings will be read on backend
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

  const handleToggleSelection = (paperId: number) => {
    const newSelection = new Set(selectedPapers);
    if (newSelection.has(paperId)) {
      newSelection.delete(paperId);
    } else {
      newSelection.add(paperId);
    }
    setSelectedPapers(newSelection);
  };

  const handleOpenSynthesis = () => {
    const paperIds = Array.from(selectedPapers);
    if (paperIds.length >= 2) {
      AppEvents.dispatchOpenSynthesisWorkbench(paperIds);
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
      <SearchBar
        query={searchQuery}
        onQueryChange={setSearchQuery}
        onSearch={handleSearch}
        isLoading={isLoading}
        placeholder="Search your library..."
        additionalInputs={
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
        }
      />

      {/* PDF Upload Section */}
      <div className="jp-jupyterlab-research-assistant-wwc-copilot-upload-section">
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,application/pdf"
          onChange={handleFileSelect}
          className="jp-jupyterlab-research-assistant-wwc-copilot-file-input"
          id="pdf-upload-input"
        />
        <label
          htmlFor="pdf-upload-input"
          className="jp-jupyterlab-research-assistant-wwc-copilot-button jp-mod-file-upload-label"
        >
          {isUploading ? 'Uploading...' : 'Upload PDF'}
        </label>
      </div>

      <ErrorDisplay error={error} />

      {/* Synthesis button - show when 2+ papers selected */}
      {selectedPapers.size >= 2 && (
        <div className="jp-jupyterlab-research-assistant-wwc-copilot-synthesis-button-container">
          <button
            onClick={handleOpenSynthesis}
            className="jp-jupyterlab-research-assistant-wwc-copilot-button jp-jupyterlab-research-assistant-wwc-copilot-synthesis-button"
          >
            Synthesize {selectedPapers.size} Studies
          </button>
        </div>
      )}

      {isLoading && <LoadingState />}

      <div className="jp-jupyterlab-research-assistant-wwc-copilot-papers">
        {papers.length === 0 && !isLoading && (
          <div className="jp-jupyterlab-research-assistant-wwc-copilot-empty">
            No papers found. Use the Discovery tab to search and import papers,
            or upload a PDF above.
          </div>
        )}
        {papers.map(paper => (
          <PaperCard
            key={getPaperKey(paper)}
            paper={paper}
            onViewDetails={() => setSelectedPaper(paper)}
            selected={paper.id !== undefined && selectedPapers.has(paper.id)}
            onToggleSelection={
              paper.id !== undefined
                ? () => handleToggleSelection(paper.id!)
                : undefined
            }
          />
        ))}
      </div>
    </div>
  );
};
