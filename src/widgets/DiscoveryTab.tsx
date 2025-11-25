import React, { useState } from 'react';
import { IPaper, searchSemanticScholar, importPaper } from '../api';
import { PaperCard } from './PaperCard';
import { showError, showSuccess } from '../utils/notifications';
import { SkeletonLoader } from './SkeletonLoader';

export const DiscoveryTab: React.FC = () => {
  const [query, setQuery] = useState('');
  const [year, setYear] = useState('');
  const [results, setResults] = useState<IPaper[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async () => {
    if (!query.trim()) {
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await searchSemanticScholar(
        query,
        year || undefined,
        20
      );
      setResults(response.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleImport = async (paper: IPaper) => {
    try {
      await importPaper(paper);
      showSuccess('Paper Imported', `Successfully imported: ${paper.title}`);
    } catch (err) {
      showError(
        'Import Failed',
        err instanceof Error ? err.message : 'Unknown error occurred',
        err instanceof Error ? err : undefined
      );
    }
  };

  return (
    <div className="jp-jupyterlab-research-assistant-wwc-copilot-discovery">
      <div className="jp-jupyterlab-research-assistant-wwc-copilot-search-bar">
        <input
          type="text"
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyPress={e => {
            if (e.key === 'Enter') {
              handleSearch();
            }
          }}
          placeholder="Search Semantic Scholar..."
          className="jp-jupyterlab-research-assistant-wwc-copilot-input"
        />
        <input
          type="text"
          value={year}
          onChange={e => setYear(e.target.value)}
          placeholder="Year (e.g., 2020-2024)"
          className="jp-jupyterlab-research-assistant-wwc-copilot-input"
        />
        <button
          onClick={handleSearch}
          disabled={isLoading || !query.trim()}
          className="jp-jupyterlab-research-assistant-wwc-copilot-button"
        >
          {isLoading ? 'Searching...' : 'Search'}
        </button>
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

      {!isLoading && (
        <div className="jp-jupyterlab-research-assistant-wwc-copilot-results">
          {results.map(paper => (
            <PaperCard
              key={paper.paperId || paper.id}
              paper={paper}
              onImport={() => handleImport(paper)}
            />
          ))}
        </div>
      )}
    </div>
  );
};
