import React, { useState } from 'react';
import { IPaper, searchSemanticScholar, importPaper } from '../api';
import { PaperCard } from './PaperCard';
import { showError, showSuccess } from '../utils/notifications';
import { SearchBar } from './SearchBar';
import { ErrorDisplay } from './ErrorDisplay';
import { LoadingState } from './LoadingState';
import { getPaperKey } from '../utils/paper';

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
      <SearchBar
        query={query}
        onQueryChange={setQuery}
        onSearch={handleSearch}
        isLoading={isLoading}
        placeholder="Search Semantic Scholar / OpenAlex..."
        additionalInputs={
          <input
            type="text"
            value={year}
            onChange={e => setYear(e.target.value)}
            placeholder="Year (e.g., 2020-2024)"
            className="jp-jupyterlab-research-assistant-wwc-copilot-input"
          />
        }
      />

      <ErrorDisplay error={error} />

      {isLoading && <LoadingState />}

      {!isLoading && (
        <div className="jp-jupyterlab-research-assistant-wwc-copilot-results">
          {results.map(paper => (
            <PaperCard
              key={getPaperKey(paper)}
              paper={paper}
              onImport={() => handleImport(paper)}
            />
          ))}
        </div>
      )}
    </div>
  );
};
