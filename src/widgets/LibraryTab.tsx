import React, { useState, useEffect } from 'react';
import { Paper, getLibrary, searchLibrary } from '../api';
import { PaperCard } from './PaperCard';

export const LibraryTab: React.FC = () => {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

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
      </div>

      {error && (
        <div className="jp-jupyterlab-research-assistant-wwc-copilot-error">
          Error: {error}
        </div>
      )}

      {isLoading && (
        <div className="jp-jupyterlab-research-assistant-wwc-copilot-loading">
          Loading...
        </div>
      )}

      <div className="jp-jupyterlab-research-assistant-wwc-copilot-papers">
        {papers.length === 0 && !isLoading && (
          <div className="jp-jupyterlab-research-assistant-wwc-copilot-empty">
            No papers found. Use the Discovery tab to search and import papers.
          </div>
        )}
        {papers.map(paper => (
          <PaperCard key={paper.id} paper={paper} />
        ))}
      </div>
    </div>
  );
};
